import random
import csv
import os

print('Starting...')

class finnish_people_generator:
    main_data_dir = 'c:\\fakedata-fi'  # Change based on your file location

    # Weighted name picker lists
    #  wsl = weighted select list
    weights_male_first = []
    weights_female_first = []
    weights_last = []
    # dict = dictionaries (in list form) that map numbers in the wsl to actual names
    names_male_first = []
    names_female_first = []
    names_last = []
    
    
    def load_people_objects(self):
        # Male first (given) names
        male_fn_file = os.sep.join((self.main_data_dir,'csv','etunimitilasto-2020-02-06-miehet.csv'))
        with open(male_fn_file,encoding='utf8') as infile:
            inreader = csv.reader(infile)
            next(inreader)  # skip the header row
            ctr = 0
            for row in inreader:
                (fname,weight) = (row[0],int(row[1].replace(",","")))
                self.names_male_first.append(fname)
                self.weights_male_first.append(weight)
                ctr += 1

        # Female first (given) names
        female_fn_file = os.sep.join((self.main_data_dir,'csv','etunimitilasto-2020-02-06-naiset.csv'))
        with open(female_fn_file,encoding='utf8') as infile:
            inreader = csv.reader(infile)
            next(inreader)  # skip the header row
            ctr = 0
            for row in inreader:
                (fname,weight) = (row[0],int(row[1].replace(",","")))
                self.names_female_first.append(fname)
                self.weights_female_first.append(weight)
                ctr += 1

        # Last (family) names
        family_name_file = os.sep.join((self.main_data_dir,'csv','sukunimitilasto-2020-02-06.csv'))
        with open(family_name_file,encoding='utf8') as infile:
            inreader = csv.reader(infile)
            next(inreader)  # skip the header row
            ctr = 0
            for row in inreader:
                (lname,weight) = (row[0],int(row[1].replace(",","")))
                self.names_last.append(lname)
                self.weights_last.append(weight)
                ctr += 1

    def get_a_name(self, gender=None):
        """
        Returns a name in (given,family) tuple.
        Randomly picks a gender if none is specified
        Gender is in English - "m" or "f"
        """
        lname = random.choices(self.names_last, self.weights_last)[0]
        fname = None
        if gender is None:
            gender = random.choice(['f','m'])
        if gender == 'm':
            fname = random.choices(self.names_male_first, self.weights_male_first)[0]
        else:
            fname = random.choices(self.names_female_first, self.weights_female_first)[0]
        
        return((fname,lname))


    def __init__(self):
        random.seed()
        self.load_people_objects()
                                 

class finnish_addresses_generator:
    main_data_dir = 'c:\\fakedata-fi'
    
    postal_code_to_city = {}
    postal_code_addresses = {}  # {post code: [(street,unit,lat,long)....] }
    population_by_postal_code = {}  # {post code: (total pop, male pop, female pop)}
    
    def load_postal_code_city(self):
        file_loc = os.sep.join((self.main_data_dir,'posti','PCF_20200523.dat'))
        with open(file_loc) as infile:    # This file is ANSI encoded
            for row in infile.readlines():
                postcode = row[13:18] # Fixed width file
                city_fi = row[179:199].strip()
                self.postal_code_to_city[postcode] = city_fi
    
    def load_population_stats(self):
        file_loc = os.sep.join((self.main_data_dir,'csv','001_12ey_2018.csv'))
        with open(file_loc, encoding='utf8') as infile:
            csv_reader = csv.reader(infile)
            next(csv_reader)
            for row in csv_reader:
                (postal_code_area,total_population,male_population,female_population) = row
                postal_code = postal_code_area[0:5]
                # Right now, this just uses total population
                self.population_by_postal_code[postal_code] = int(total_population)
        
    def load_postal_code_addresses(self, postal_code):
        # To save memory, this procedure loads addresses by the first number of a postal code.
        # If you call this procedure and the necessary posal code is already loaded - then it just does nothing
        dict_length = len(self.postal_code_addresses.keys())
        keys = list(self.postal_code_addresses.keys())
        if dict_length > 0 and keys[0][0] == postal_code[0]:
            return None
        self.postal_code_addresses = {}
        file_loc = os.sep.join((self.main_data_dir,'openaddr-collected-europe','fi','countrywide-fi.csv'))
        if not os.path.exists(file_loc):
            raise Exception('\n***You will need to download address files from openaddresses.io.  Please see the openaddr-collected-europe subdirectory for details.')
        with open(file_loc, encoding='utf8') as infile:
            csv_reader = csv.reader(infile)
            next(csv_reader)
            for row in csv_reader:
                (long,lat,addr_number,street,unit,city,district,region,postcode,rowid,rowhash) = row
                if postcode[0] == postal_code[0]:
                    # Add it to the dictionary
                    if postcode not in self.postal_code_addresses:
                        self.postal_code_addresses[postcode] = []
                    self.postal_code_addresses[postcode].append((street,addr_number,long,lat))

    def get_address_in_postal_code(self,postal_code):
        # The postal code population file is only good at 4-digit granularity
        self.load_postal_code_addresses(postal_code)

        potential_postal_codes = []
        potential_weights = [] # number of units per postal code
        
        for pca_code in self.postal_code_addresses:
            if pca_code[0:4] == postal_code[0:4]:
                potential_postal_codes.append(pca_code)
                potential_weights.append(len(self.postal_code_addresses[pca_code]))
        
        chosen_code = random.choices(potential_postal_codes,weights=potential_weights)[0]
        
        if chosen_code not in self.postal_code_addresses:
            return ('','',25.0,66.5)
        else:
            return random.choice(self.postal_code_addresses[chosen_code])
    
    def __init__(self):
        random.seed()
        self.load_postal_code_city()
        self.load_population_stats()

outdir = 'c:\\fakedata-fi\\output'

fp = finnish_people_generator()
fa = finnish_addresses_generator()

people_per_postcode = fa.population_by_postal_code

postcode_keys = sorted(people_per_postcode.keys())

with open(os.sep.join((outdir,'fakepeople_fi.csv')),mode='w',encoding='utf8', newline='') as ow: # change the newline if using Linux
    cw = csv.writer(ow)
    for postcode in postcode_keys:
        print('Processing {0}'.format(postcode))
        population = people_per_postcode[postcode]
        sample_rate = .05
        for i in range(int(population * sample_rate)):
            (first_name,last_name) = fp.get_a_name()
            (street,unit,lat,long) = fa.get_address_in_postal_code(postcode)
            city = fa.postal_code_to_city[postcode]
            row = (first_name,last_name,street,unit,city,postcode,lat,long)
            cw.writerow(row)



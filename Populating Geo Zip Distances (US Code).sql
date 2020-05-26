--drop table dbo.LatitudeAdjustment_4326


--create table dbo.LatitudeAdjustment_4326 ([LatitudeIndex] int primary key, LongitudeDegreeDist float, LatitudeDegreeDist float)
--GO

declare @latitudeid int, @latitudeFloat float, @distanceLong float, @distanceLat float, @point1 geography, @point2 geography

set @latitudeid = -8999

while @latitudeid < 9000
begin
	set @latitudeFloat = @latitudeid / 100.0	
	set @point1 = geography::Point(@latitudeFloat,0.00,4326)
	set @point2 = geography::Point(@latitudeFloat,1.00,4326)
	set @distanceLong = @point1.STDistance(@point2)
	set @point2 = geography::Point(@latitudeFloat + 0.01, 0.00, 4326)
	set @distanceLat = @point1.STDistance(@point2) * 100.0
	insert into dbo.LatitudeAdjustment_4326 values (@latitudeid, @distanceLong, @distanceLat)
	set @latitudeid = @latitudeid + 1
end

select * from dbo.LatitudeAdjustment_4326

SELECT
Z1.ZIP as ZIP1, Z2.ZIP as ZIP2, 
  SQRT (
       POWER((Z2.Center_Latitude - Z1.Center_Latitude) * L.LatitudeDegreeDist ,2)  +
	   POWER((Z2.Center_Longitude - Z1.Center_Longitude) * L.LongitudeDegreeDist ,2) 
	   ) / 1000 as DIST_KM
INTO dbo.ZIP_Distance_Map
FROM dbo.ZIPCenters Z1
JOIN dbo.ZIPCenters Z2 ON ABS(Z2.Center_Latitude - Z1.Center_Latitude) < 2 AND ABS(Z2.Center_Longitude - Z1.Center_Longitude) < 3
JOIN dbo.LatitudeAdjustment_4326 L on FLOOR((Z2.Center_Latitude + Z1.Center_Latitude) * 50) = L.LatitudeIndex;

CREATE EXTERNAL TABLE dbo.ZIP_Distance_Map_External
(
	ZIP1					CHAR(5) NOT NULL,
	ZIP2				CHAR(5) NOT NULL,
	Distance_KM			float
)
WITH
(LOCATION = '/zip_distances.txt',
 DATA_SOURCE = GeoAzureBlob,
 FILE_FORMAT = CSVNoQuotes
)
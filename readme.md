Hello , 

This can run in a production environment . But has been made and tested on local at a personal capacity.production level code.
It can generate and handle large volumn of data . programmed accordingly.
It has encryption , logging , spark fundamentals , raises exception
used aws sdk boto3 to access S3 for reading , deleting , pushing , pull and other activites

airflow , CI /CD pipeline can also be added but not in the scope of the project

includes some concepts of data modelling

uses star schema - 1 fact table and 4 dimension table
schema checking 
json , csv 
parquet 
s3 data mart
snappy algorithm to decompress
partition level

con - downloaded on local 
few more loose ends


software requirement - my sql server , my sql workbench , hadoop

used openjdk@11
setting up spark and hadoop with java and python , environment variable


What is it about ?
end to end data engineering which is worked on daily professional life.
for a particular team where a specific DE Team is sitting before you and a different one after you tackling diff DE work.

Production grade project - Encryption , logging , boto3 sdk , data mart

Interview related -

Data generated from a transactional system
Reading from S3
Transformed based on use case provided
writing/loading in data mart

why?
To collect POS/POC billing person contact connected with customer
and incentivize it.
To tracking customer spend / activity
daily/monthly report

How?
- Spark has been used for transformation.
- Data volumn generated has been set to 15gb per day but could be    flexible as this should work on much higher volumn also.
- S3 boto3 sdk has been used to connect with S3.S3 doesnot have direct access to S3 console but programmatically where this software will have user created and access keys will be provided to work.
- Data pushed /loaded into Data mart(used for segregating in different groups) for reporting tool to further process/analytics.

Understanding the Data 
Our team is the requirement that transactional data be present in S3.

Fact table - 
Schema - Field and Type  of data in the table
- This fact table will have customer related data , store id , product data , sales data , pos id , price , cost 
- Customer transactional actual data
- get this data daily/monthly from s3

Dimension table - 
Gives context , small table relative to fact so maybe used as broadcast table when spark join.
- customer profile personal data.
- joining date or first purchase date.
- customer id is primary key which will be foreign key in transact data
- same for store id 
- randomly generated data .

Dimension table 
Store table data
manager , address , store opened.

Dimension table
product id , info , price details 
- not implemented here as it becomes big
- SCD2 logic here as we will have current price and old price data here which changes
- inventory manage here with product expiry dates provided

Dimension table 
Sales / billing table which is POC/POS for which we are doing all of it.
schema - id , name , manager(heirarchy , could be manager of manager) , address , joining date.
- billing person may also shift to different store
- data is dynamically generated

Staging table ( For auditing and process table)
-  if status active then failed in between, if inactive then process completed
- info about stages

7th table - Customer data mart
use for creating dynamic coupon code.
- two new column data introduced with total sales per month
- to think about how to make customer shopping behavior consistent.
- not scope of this project

sales team data mart
sales data and new data generated of incentive of 1% to top performer
based on total sales done.


what directory in local and in aws s3 to read and write . 
project directory structure.
encryption decyption aws access key for the project 
generate high volumn of different csv files data.custom code to generate it.
connect to s3 using boto3 client and list object bucket

important
********************
- con - how and why do we need to download data on local 
*********************

1.setting up git and github , venv
2.pip install requirements .txt for installing dependencies . 
aws IAM user access for s3
create IAM user - s3 full access user group -> access key for the user via Local code 
3.encryption decryption 
4.access key either stored in config.py as encrypted like here or in vault 
5. password set at os level via environment variable
6. two project directory required - local and aws
7. random csv data generated of sales.
8. connect to boto3 client for s3 connection
9.transformations > main.py which takes  utility , config, s3 , logging 
10. writing modular code using function and class
11. connecting mysql DB through python
12. -------check for failure and previous process status as logs . as these processess are run frequently In production --------------------------- 
13. -------con : Notification not done here for process status and especially if it fails. will be done later on . sql used
14. staging table to figure out if last run was successful or failure
15. logger segregates different logs based if error , debugging , info and also provides time of running 
vs if we just use print
16. logging data can be save in a csv . 
17. encrypted keys is still public on github so a con
18. s3_client is object 
19. product staging table if production breaks in between
20. status inactive means process faied in between . has filename also.
21 .?????????? manually create mysql databases and write tables ???????????
    manually "CREATE TABLE product_staging_table" was done . could be dynamic

22. con -  not done here - providing an error if status inactive table and not process the next file 
23. con - hardcoded sql database details because of doing it in local

24. jdbc driver by java used for my sql connection 
25. mysql cli 
show databases;
create database mysql_aws_pyspark_db;
use mysql_aws_pyspark_db;
create table ....;
26. till now able to initialize s3 client with decrypting aws keys , mysql connection and querying , able to check local directories for file . 
27. next step - read all files in s3 and throwing error if not . creating spark session 
28. ------con : as we are downloading the file on local as we were not able to directly get spark to connect and read from s3
could be done to improve this.
ask infra or devops team for how to connect path of spark and s3
29. so first downloading from s3 , reading it via spark and deleting it later.
cost huge for large files
30. check in s3 for it to be csv files
---- con : could be multiple types of files like parquet which requires more improvement
31. ----con : bucket name should be dynamically get from table as bucket name will come from different source who has put up the data for us to read.(config.py)

32.  moving csv file which contains randomly generated data to s3 .
33. logger response is in json . could be better formated .
34. reading from s3
35. agree upon on csv file so no unwanted files or we can trim later

downloading from s3

Get a list of all files in the local directory
Filter only csv files and creating absolute paths.

------------spark will be required for huge loads of data. here it is very tiny


---- so much processing before reaching spark transformation


schema validation
--------con---could be done - handling additional columns , maybe join together in one extra column
setting null for missing values or columns , depends on the use case.

------con---- could be done for extra or less column files -> currently in error
may be processed later on.

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
3.encryption decryption 
4.access key either stored in config.py as encrypted like here or in vault 
5. password set at os level via environment variable
6. two project directory required - local and aws
7. random csv data generated of sales.


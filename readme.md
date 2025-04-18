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

apache-spark--3.5.5

this error when
"The operation couldn’t be completed. Unable to locate a Java Runtime.
Please visit http://www.java.com for information on installing Java."
for source .zprofile
the file has export JAVA_HOME=$(/usr/libexec/java_home -v 11) .
I changed it after installing brew install openjdk@11 and uninstalled oracle java 24.0.1 


export JAVA_HOME=$(/usr/libexec/java_home -v 11)
export PATH=$JAVA_HOME/bin:$PATH
export PATH="$(brew --prefix)/opt/openjdk@11/bin:$PATH"

eval "$(/opt/homebrew/bin/brew shellenv)"
export PATH="${PATH}:/usr/local/mysql-9.3.0-macos15-arm64/bin/"
export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
export CPPFLAGS="-I/opt/homebrew/opt/openjdk@11/include"
export HADOOP_HOME=/opt/homebrew/Cellar/hadoop/3.4.1
export PATH=$PATH:$HADOOP_HOME/bin



export HADOOP_HOME=/opt/homebrew/Cellar/hadoop/3.4.1
export PATH=$PATH:$HADOOP_HOME/bin
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop


export SPARK_HOME=`brew info apache-spark | grep /usr | tail -n 1 | cut -f 1 -d " "`/libexec
export PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH


export HADOOP_HOME=`brew info hadoop | grep /usr | head -n 1 | cut -f 1 -d " "`/libexec
export LD_LIBRARY_PATH=$HADOOP_HOME/lib/native/:$LD_LIBRARY_PATH

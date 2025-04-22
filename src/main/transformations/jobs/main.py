import sys , os
sys.path.append(os.path.abspath("/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws"))
from resources.dev import config
from src.main.utility.encrypt_decrypt import *
from src.main.utility.s3_client_object import S3ClientProvider
from src.main.utility.logging_config import *

from src.main.utility.mysql_session import *

from src.main.read.read_from_s3 import *

from src.main.download.download_from_s3 import *

from src.main.utility.spark_session import *

import shutil
from src.main.move.move_files import *
import datetime

from src.main.read.database_read import *
from src.main.transformations.jobs.dimension_tables_join import *

from src.main.write.dataframe_writer import *
from src.main.upload.upload_to_s3 import *

from src.main.transformations.jobs.customer_mart_sql_tranform_write import *
from src.main.transformations.jobs.transactions_mart_sql_transform_write import *
from src.main.delete.local_file_delete import *
from src.main.delete.aws_delete import *
from src.main.delete.database_delete import *


#Get S3 Client
aws_access_key = config.aws_access_key
aws_secret_key = config.aws_secret_key

s3_client_provider = S3ClientProvider(decrypt(aws_access_key),decrypt(aws_secret_key))
s3_client = s3_client_provider.get_client()

response = s3_client.list_buckets()
#print(response)
logger.info("List of Buckets: %s", response['Buckets'])

# S3 -> local -> S3
#check if local directory has already a  file . if not present then success.
#check if same file present in staging area and what is the status there .rerun and dont delete if status A 


csv_files = [file for file in os.listdir(config.file_from_s3_local_directory) if file.endswith(".csv")]
connection = get_mysql_connection()
cursor = connection.cursor()

total_csv_files = []
if csv_files:
    # for file in csv_files:
    #     total_csv_files.append(file)

    # to check status active for item_staging_table in mysql db which means fail
    statement = f"""
    select distinct file_name 
    from {config.database_name}.{config.item_staging_table}
    where file_name in ({str(csv_files)[1:-1]}) and status = 'A'
    
    """
    
    logger.info(f"sql statement created:{statement} ")
    cursor.execute(statement)
    data = cursor.fetchall()
    if data:
        logger.info("Your last iteraton was failed please check")
    else:
        logger.info("No record ")



else:
    logger.info("Last iteration was success! or this is the Beginning")


try:
    s3_reader = S3Reader()
    folder_path = config.s3_source_directory
    s3_absolute_file_path = s3_reader.list_files(s3_client,config.bucket_name,folder_path)  
     #config.bucket_name could be dynamically generated

    logger.info("Absolute path on s3 bucket for csv file %s ",s3_absolute_file_path)
    if not s3_absolute_file_path:
        logger.info(f"No files available at {folder_path}")
        raise Exception("No Data available to process ")
    
except Exception as e:
    logger.error("Exited with error:- %s",e)
    raise e



#2025-04-19 15:57:13,414 - INFO - Absolute path on s3 bucket for csv file ['s3://aws-pyspark-pr-1/transaction_data/transactions_data.csv', 's3://aws-pyspark-pr-1/transaction_data/transactions_data.csv']

          
bucket_name = config.bucket_name
local_directory = config.file_from_s3_local_directory

# downloading from s3
prefix = f"s3://{bucket_name}/"
file_paths = [url[len(prefix):] for url in s3_absolute_file_path] 
logging.info(f"FIle path available on s3 under %s bucket and folder name is %s",bucket_name,local_directory)
logging.info(f"File path available on s3 under {bucket_name} bucket and folder name is {file_paths}")

try:
    downloader = S3FileDownloader(s3_client,bucket_name,local_directory)
    downloader.download_files(file_paths)
except Exception as e:
    logger.error("File download error: %s",e)
    sys.exit()



#Get a list of all files in the local directory
all_files = os.listdir(local_directory)
logger.info(f"List of files present at my local directory after download{all_files}")

#Filter only csv files and creating absolute paths.

if all_files:
    csv_files = []
    error_files = []
    for file in all_files:
        if file.endswith(".csv"):
            csv_files.append(os.path.abspath(os.path.join(local_directory,file)))
        else:
            error_files.append(os.path.abspath(os.path.join(local_directory,file)))

    if not csv_files:
        logger.error("No csv data available to process the request")
        raise Exception("No csv data available to process the request")
    
else:
    logger.error("There is no data to process.")
    raise Exception("There is no data to process.")

#csv_files = str(csv_files)[1:-1]

logger.info("*************Listing the File************************************")
logger.info("List of csv files that needs to be be processed %s",csv_files)

logger.info("*********************************Creating Spark session*******************************")

spark = spark_session()

logger.info("***********************spark session created ***************************")


#schema validation
# either in error file or make a dataframe out of it


logger.info("************Checking schema for data loaded in s3*************")


correct_files = []
for data in csv_files:
    data_schema = spark.read.format("csv")\
                        .option("header","true")\
                        .load(data).columns
    logger.info(f"Schema for the {data} is {data_schema}")
    logger.info(f"Mandatory column schema is {config.mandatory_columns}")
    missing_columns = set(config.mandatory_columns) - set(data_schema)
    logger.info(f"missing columns are {missing_columns}")

    if missing_columns:
        error_files.append(data)

    else:
        logger.info(f"No missing column for the {data} ")
        correct_files.append(data)


logger.info(f"************List of correct Files*****{correct_files}")
logger.info(f"************List of error Files*****{error_files}")
logger.info(f"************Moving error data to error directory if any to local*****")


#Move the data to error directory on local and s3



error_folder_local_path = config.error_folder_path_local 
if error_files:
    for file_path in error_files:
        if os.path.exists(file_path):
            file_name = os.path.basename (file_path)
            destination_path = os.path.join(error_folder_local_path, file_name)
            
            shutil.move(file_path, destination_path)
            logger.info(f"Moved '{file_name}' from s3 file path to '{destination_path}'.")

            source_prefix = config.s3_source_directory
            destination_prefix = config.s3_error_directory

            message = move_s3_to_s3(s3_client, config.bucket_name, source_prefix,destination_prefix)
            logger.info(f" {message}")
        else:
            logger.error(f"'{file_path}' does not exist.")
else:
    logger.info("There is no error files available at our dataset *********")




#Additional columns needs to be taken care of
# Determine extra columns

#Before running the process
#stage table needs to be updated with status as Active (A) or inactive (1) 
logger.info(f"*** Updating the item_staging_table that we have started the process *********")
insert_statements = []
db_name =config.database_name
current_date = datetime.datetime.now()
formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
if correct_files:   
    for file in correct_files:
        filename = os.path.basename(file)
        statements= f"""
        INSERT INTO {db_name}.{config.item_staging_table}
        (file_name, file_location, created_date, status)
        VALUES (%s,%s,%s,%s)
        """

        insert_statements.append(statements)
    
    logger.info(f"Insert statement created for staging table --- {insert_statements}") 
    logger.info("*** *****Connecting with Mysql**************")
    connection = get_mysql_connection()
    cursor = connection.cursor()
    logger.info("********* Mysql  connected successfully*******")
    for statement in insert_statements:
        cursor.execute(statement,(filename, filename, formatted_date,'A'))
        connection.commit()
    cursor.close()
    connection.close()
else:

    logger.error("********** There is no files to process ************")
    raise Exception("*** No Data avalable with correct files*****")





logger.info("**** Staging table updated successfully *****")
logger.info("*****Fixing extra column coming from source**")


schema = StructType([
        
        StructField("customer_id", IntegerType(), True),
        StructField("store_id", IntegerType(), True),
        StructField("item_name", StringType(), True),
        StructField("Transactions_date", DateType(), True),
        StructField("Transactions_person_id", IntegerType(), True),
        StructField("price", FloatType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("total_cost", FloatType(), True),
        StructField("additional_column", StringType(), True)

        ])



#connecting with DatabaseReader
# database_client = DatabaseReader(config.url, config.properties)
# logger.info("****
# ***** creating empty dataframe ****
# *")
# final_df_to_process = database_client.create_dataframe(spark, "empty_df_create_table")


final_df_to_process = spark.createDataFrame([], schema=schema)
# Create a new column with concatenated values of extra columns

for data in correct_files:
    data_df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(data)
    data_schema = data_df.columns
    extra_columns = list(set(data_schema) - set (config.mandatory_columns))
    logger.info(f"Extra columns present at source is {extra_columns}")
    if extra_columns:
        data_df = data_df.withColumn ("additional_column", concat_ws(", ",*extra_columns))\
            .select("customer_id","store_id","item_name", "Transactions_date","Transactions_person_id",
            "price", "quantity","total_cost","additional_column") 
        logger.info(f"processed {data} and added 'additional_column'")

    else:
        data_df = data_df.withColumn ("additional_column", lit (None))\
            .select("customer_id", "store_id", "item_name","Transactions_date","Transactions_person_id",
                "price", "quantity", "total_cost" ,"additional_column")
      
    final_df_to_process = final_df_to_process.union(data_df)
# final_df_to_process = data_df
logger.info("*********Final Dataframe from source which will be going to processing**** ")
final_df_to_process.show()


#Cleaning and segregating of the data has been done -> Processing and transformation of data will be done in the next part
#  fetching dimension tables to enrich fact transaction table -> write to local and upload to S3 . will be creating partitions

# Two different data mart will be created - customer , transactions(transactions)
# datamart are for two different types of specific data category
#customer buying behaviour with store id segregation using partition . 
# frequency - monthly


#Connecting with DatabaseReader
database_client = DatabaseReader (config.url, config.properties)
 #creating df for all tables
#customer table
logger.info("**********Loading customer table into customer_table_df*******")
customer_table_df = database_client.create_dataframe(spark, config.customer_table_name) 
#item table
logger.info("*********Loading item table into item_table_df **********")
item_table_df = database_client.create_dataframe (spark, config.item_table)


#item_staging_table 
logger.info("****** Loading satging table into item_staging_table_df******")
item_staging_table_df = database_client.create_dataframe (spark, config.item_staging_table)

#transactions_team table
logger.info("****** Loading transactions team table into transactions_team_table_df")
transactions_team_table_df = database_client.create_dataframe (spark, config.transactions_team_table)

#store table
logger.info("****Loading store table into store_table_df *")
store_table_df = database_client.create_dataframe (spark, config.store_table)

s3_customer_store_transactions_df_join = dimesions_table_join(final_df_to_process,
                                                        customer_table_df, 
                                                        store_table_df,
                                                        transactions_team_table_df)



#Final enriched data
logger.info("**********Final Enriched Data *************")
s3_customer_store_transactions_df_join.show()


#writing customer data into customer data mart in parquet format
# first in local -> s3 for other downstream work -> writing downstream analytics data into mysql db server tables 


logger.info("***write the data into Customer Data Mart ******")
final_customer_data_mart_df = s3_customer_store_transactions_df_join\
                            .select("ct.customer_id",
                                    "ct.first_name","ct.last_name","ct.address",
                                    "ct.pincode", "phone_number",
                                    "transactions_date", "total_cost")
logger.info("**** Final Data for customer Data Mart******")


final_customer_data_mart_df.show()


parquet_writer = ParquetWriter("overwrite", "parquet")
parquet_writer.dataframe_writer(final_customer_data_mart_df,config.customer_data_mart_local_file)


 
logger.info(f"*******customer data written to local disk at {config.customer_data_mart_local_file} in parquet *******")


#Move data on s3 bucket for customer_data_mart from local
logger.info(f"**** Data Movement from local to s3 for customer data mart *******")
s3_uploader = UploadToS3 (s3_client)
s3_directory = config.s3_customer_datamart_directory
message =s3_uploader.upload_to_s3(s3_directory, config.bucket_name, config.customer_data_mart_local_file)
logger.info(f" {message}")



#transactions_team Data Mart
logger.info("**** write the data into transactions team Data Mart ******* ")
final_transactions_team_data_mart_df = s3_customer_store_transactions_df_join\
                        .select("store_id",
                        "transactions_person_id","transactions_person_first_name","transactions_person_last_name", "store_manager_name", "manager_id","is_manager",
                        "transactions_person_address", "transactions_person_pincode"
                        ,"transactions_date", "total_cost"
                        , expr("SUBSTRING (transactions_date,1,7) as transactions_month"))

logger.info("**** Final Data for transactions team Data Mart*******")
final_transactions_team_data_mart_df.show()
parquet_writer.dataframe_writer (final_transactions_team_data_mart_df,config.transactions_team_data_mart_local_file)
logger.info(f"****transactions team data written to local disk at {config.transactions_team_data_mart_local_file}********")


                                                        

#Move data on s3 bucket for transactions_data_mart
s3_directory = config.s3_transactions_datamart_directory
message =s3_uploader.upload_to_s3 (s3_directory,
                            config.bucket_name,
                            config.transactions_team_data_mart_local_file)
logger.info(f" {message}")


#Also writing the data into partitions
final_transactions_team_data_mart_df.write.format("parquet")\
                                .option("header", "true")\
                                .mode("overwrite")\
                                .partitionBy("transactions_month", "store_id")\
                                .option("path", config.transactions_team_data_mart_partitioned_local_file )\
                                .save()                                                        



#Move data on s3 for partitioned folder I
s3_prefix = "transactions_partitioned_data_mart"
current_epoch = int(datetime.datetime.now().timestamp()) * 1000
for root, dirs, files in os.walk (config.transactions_team_data_mart_partitioned_local_file):
    for file in files:
        print(file)
        local_file_path = os.path.join(root, file)
        relative_file_path = os.path.relpath(local_file_path, 
                                             config.transactions_team_data_mart_partitioned_local_file)
        s3_key = f"{s3_prefix}/{current_epoch}/{relative_file_path}"
        s3_client.upload_file(local_file_path, config.bucket_name, s3_key)






#calculation for customer data mart customer buying behaviour every month

#writing the data into MySQL table
logger.info("******Calculating customer spending every month  **")
customer_mart_calculation_table_write(final_customer_data_mart_df)
logger.info("******Calculation of customer mart done and written into the table*********")


#calculation for transactions sales team performace
logger.info("******Calculating transactions team performance every month  *****")
transactions_mart_calculation_table_write(final_transactions_team_data_mart_df)
logger.info("******Calculation of transactions team performance mart done and written into the table*********")



#Moving the file on s3 processed folder (data marts data) and delete the local files

source_prefix = config.s3_source_directory
destination_prefix = config.s3_processed_directory
message = move_s3_to_s3 (s3_client, config.bucket_name, source_prefix, destination_prefix) 
logger.info(f" {message}")

logger.info("- **** Deleting local data from local **")
delete_local_file(local_directory)
logger.info("- **** Deleting transactions data from local **")
delete_local_file(config.transactions_team_data_mart_local_file)
delete_local_file(config.transactions_team_data_mart_partitioned_local_file)
logger.info("s** Deleted transactions data from local*")


logger.info("**** Deleting customers data from local ************" )
delete_local_file(config.customer_data_mart_local_file)
logger.info("s** Deleted customers data from local*")

logger.info("**** Deleting error data from local ************" )
delete_local_file(config.error_folder_path_local)
logger.info("s** Deleted error data from local*")


#update the status of staging table update_statements = []
update_statements =[]
if correct_files:
                for file in correct_files:
                    filename = os.path.basename(file)
                    statements = f"UPDATE {db_name}.{config.item_staging_table}"\
                          f" SET status = 'I',updated_date='{formatted_date}' "\
                          f"WHERE file_name = '{filename}'"
                    update_statements.append(statements)
                
                logger.info(f"Updated statement created for staging table --- {update_statements}") 
                logger.info("*** *****Connecting with My SQL server **")
                connection = get_mysql_connection()
                cursor = connection.cursor()
                logger.info("*****    My SQL server connected successfully ********")


                for statement in update_statements:
                    cursor.execute(statement)
                    connection.commit()
                cursor.close()
                connection.close()
else:
    logger.error("* *****  There is some error in process in between****")
    sys.exit()


input("Press enter to terminate ")  #for spark

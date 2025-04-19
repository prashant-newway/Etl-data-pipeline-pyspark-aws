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
    directory_path = config.s3_source_directory
    s3_absolute_file_path = s3_reader.list_files(s3_client,config.bucket_name,folder_path = directory_path)   #config.bucket_name could be dynamically generated

    logger.info("Absolute path on s3 bucket for csv file %s ",s3_absolute_file_path)
    if not s3_absolute_file_path:
        logger.info(f"No files available at {directory_path}")
        raise Exception("No Data available to process ")
    
except Exception as e:
    logger.error("Exited with error:- %s",e)
    raise e



#2025-04-19 15:57:13,414 - INFO - Absolute path on s3 bucket for csv file ['s3://aws-pyspark-pr-1/transaction_data/sales_data.csv', 's3://aws-pyspark-pr-1/transaction_data/transactions_data.csv']

          
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
logger.info(f"*** Updating the product_staging_table that we have started the process *********")
insert_statements = []
db_name =config.database_name
current_date = datetime.datetime.now()
formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
if correct_files:   
    for file in correct_files:
        filename = os.path.basename(file)
        statements= """INSERT INTO {db_name}.{config.product_staging_table}
        (file_name, file_location, created_date, status)" 
        VALUES ('{filename}', '{filename}', '{formatted_date}','A')"""

        insert_statements.append(statements)
    
    logger.info("Insert statement created for staging table --- {insert_statements}") 
    logger.info("*** *****Connecting with My SQL server*")
    connection = get_mysql_connection()
    cursor = connection.cursor()
    logger.info("********* My SQL server connected successfully*******")
    for statement in insert_statements:
        cursor.execute(statement)
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
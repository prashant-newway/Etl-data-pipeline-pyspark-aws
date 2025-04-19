import sys , os
sys.path.append(os.path.abspath("/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws"))
from resources.dev import config
from src.main.utility.encrypt_decrypt import *
from src.main.utility.s3_client_object import S3ClientProvider
from src.main.utility.logging_config import *

from src.main.utility.mysql_session import *

from src.main.read.read_from_s3 import *



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

    # to check status inactive for item_staging_table in my sql db
    statement = f"""
    select distinct file_name 
    from {config.database_name}.{config.item_staging_table}
    where file_name in ({str(csv_files)[1:-1]}) and status = 'I'
    
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

          

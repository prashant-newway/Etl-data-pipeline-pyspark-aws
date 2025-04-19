import os

key = "key_project"
iv = "iivvv_encryption"
salt = "salt_AesEncryption"

#AWS keys
aws_access_key = "d+Qz/Oq9FFnbQpZUzsBPgxWsoDqyXvUw4+ABV8X9dE0=" 
aws_secret_key = "Co1venlNWAdSsQ4npVm2BE8oVDQh0EGQ/o9ty7nMRf6emizkryDi/XJWnhoZVct+" 


bucket_name = "aws-pyspark-pr-1"
s3_customer_datamart_directory = "customer_data_mart"
s3_transactions_datamart_directory = "transaction_data_mart"

s3_source_directory = "transaction_data/"

s3_error_directory = "transaction_data_error/"
s3_processed_directory = "transaction_data_processed/"
s3_partitioned_directory = "transaction_partitioned_data_mart/"


#Database credential
# MySQL database connection properties
database_name = "mysql_aws_pyspark_db"
url = f"jdbc:mysql://localhost:3306/{database_name}"
properties = { 
    "user": "root",
    "password": "password",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# Table name
customer_table_name = "customer"
item_staging_table = "item_staging_table"
item_table = "item"
transactions_team_table = "transactions_team"
store_table = "store"

#Data Mart details
customer_data_mart_table = "customers_data_mart"
transactions_team_data_mart_table = "transactions_team_data_mart"

# Required columns
mandatory_columns = ["customer_id","store_id","item_name","transactions_date","transactions_person_id","price","quantity","total_cost"]


# File Download location
file_from_s3_local_directory = "/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws/local_project_directory_download_location/file_from_s3/"
customer_data_mart_local_file = "/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws/local_project_directory_download_location/customer_data_mart/"
transactions_team_data_mart_local_file = "/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws/local_project_directory_download_location/transactions_team_data_mart/"
transactions_team_data_mart_partitioned_local_file = "/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws/local_project_directory_download_location/transactions_partition_data/"
error_folder_path_local = "/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws/local_project_directory_download_location/error_files/"

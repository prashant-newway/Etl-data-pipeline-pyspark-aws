# Overview

This project implements a comprehensive ETL (Extract, Transform, Load) data pipeline that simulates a production-grade data processing workflow using AWS S3, PySpark, and MySQL, and loads optimized data marts into both local storage and S3 for downstream analytics. The pipeline is designed to efficiently handle large datasets, perform complex data transformations using Spark features such as joins and partitioning, and manage data storage across both cloud and relational database environments. It includes capabilities for schema validation, data quality checks, error handling, encryption, logging, and the use of dynamic libraries.

It uses data modeling concepts to create a test dataset that follows a star schema, with one fact table containing customer transactional data stored in AWS S3, and four dimension tables (customer, item, employee, store) stored in a local MySQL database. Additionally, a staging table is used to monitor the status of the process.




# Star Schema Database ER Diagram
A star schema with one fact table and four dimension tables:

- Fact Table: Stores transactional data accessed daily/monthly from AWS S3.
- Dimension Tables: Stores Customer, Item, Employee, and Store details in local MySQL database
- Staging Table: Tracks job status and error logs during data pipeline execution.

```

┌───────────────────────┐       ┌─────────────────────┐
│ dim_customer          │       │ dim_store           │
├───────────────────────┤       ├─────────────────────┤
│ customer_id (PK)      │       │ id (PK)             │
│ first_name            │       │ address             │
│ last_name             │       │ store_pincode       │
│ address               │       │ store_manager_name  │
│ pincode               │       │ store_opening_date  │
│ phone_number          │       │ reviews             │
│ customer_joining_date │       │                     │
└────────┬──────────────┘       └────────┬────────────┘
         │                               │
         │                               │
         │                               │
         │        ┌───────────────────────────────────┐
         │        │                                   │
         │        │      fct_transactions             │
         └────────┤                                   ├───────────┐
                  │ transaction_id (PK)               │           │
                  │ customer_id (FK)                  │           │
                  │ store_id (FK)                     │           │
                  │ item_id (FK)                      │           │
                  │ transactions_person_id (FK)       │           │
                  │ transactions_date                 │           │
                  │ price                             │           │
                  │ quantity                          │           │
                  │ total_cost                        │           │
                  └───────────────────────────────────┘           │
                           ▲                                      │
                           │                                      │
         ┌─────────────────┘                                      │
         │                                                        │
┌────────┴──────────┐                            ┌────────────────┴───────────┐
│ dim_item          │                            │ dim_transactions_person     │
├───────────────────┤                            ├────────────────────────────┤
│ id (PK)           │                            │ id (PK)                    │
│ name              │                            │ first_name                 │
│ current_price     │                            │ last_name                  │
│ old_price         │                            │ manager_id                 │
│ created_date      │                            │ is_manager                 │
│ updated_date      │                            │ address                    │
│ expiry_date       │                            │ pincode                    │
│                   │                            │ joining_date               │
└───────────────────┘                            └────────────────────────────┘
```


### Additional Tables

- **Staging Table:** For auditing and process tracking
- **Customer Data Mart:** Aggregated customer spending patterns with dynamically generated promotion codes
- **Transcations Sales Team Data Mart:** Performance metrics with incentive calculations for top performers


### Local mysql db table description of staging tables and data marts:
![Alt text](https://github.com/prashant-newway/Etl-data-pipeline-pyspark-aws/blob/main/mysql_local_db_tables.png?raw=true)


# Project Directory Tree

```
.
├── directory_tree.txt
├── local_project_directory_download_location
│   ├── customer_data_mart
│   ├── error_files
│   ├── file_from_s3
│   ├── transactions_partition_data
│   └── transactions_team_data_mart
├── mysql_local_db_tables.png
├── random_generated_data
│   └── transactions_data.csv
├── readme.md
├── resources
│   ├── dev
│   │   ├── config.py
│   │   └── requirements.txt
│   └── sql_scripts
│       └── table_scripts.sql
├── spark jobs screenshot.png
└── src
    ├── main
    │   ├── delete
    │   │   ├── aws_delete.py
    │   │   ├── database_delete.py
    │   │   └── local_file_delete.py
    │   ├── download
    │   │   └── download_from_s3.py
    │   ├── move
    │   │   └── move_files.py
    │   ├── read
    │   │   ├── database_read.py
    │   │   └── read_from_s3.py
    │   ├── transformations
    │   │   └── jobs
    │   │       ├── customer_mart_sql_tranform_write.py
    │   │       ├── dimension_tables_join.py
    │   │       ├── main.py
    │   │       └── transactions_mart_sql_transform_write.py
    │   ├── upload
    │   │   └── upload_to_s3.py
    │   ├── utility
    │   │   ├── encrypt_decrypt.py
    │   │   ├── logging_config.py
    │   │   ├── mysql_session.py
    │   │   ├── s3_client_object.py
    │   │   └── spark_session.py
    │   └── write
    │       ├── database_write.py
    │       └── dataframe_writer.py
    └── test
        ├── generate_csv_data.py
        ├── generate_customer_table_data.py
        └── transactions_data_upload_s3.py

23 directories, 30 files


```

# ETL Data Flow

```
┌─────────────────────────────────────────────────────────┐
│Transaction sales data is available in S3(used Test Data)│
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Status check of last ran process (success/failure)      │
│ in the staging table data in local MySQL DB             │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Download data from AWS S3 bucket                        │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Store in Local Directory after data validation          │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Creation of Spark session and checking of schema        │
│ of S3 transaction files                                 │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Handling correct and error files                        │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Staging table status update in MySQL local database     │
│ of this ETL process                                     │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Creating Spark DataFrame with handling of               │
│ additional columns, if any                              │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Loading dimension table from MySQL local DB             │
│ and creating Spark DataFrames                           │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Joining all Spark DataFrames from dimension table       │
│ from local MySQL DB and transaction table from S3       │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Selecting columns for different datamarts creation      │
│ and ingesting parquet files into local and S3           │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Writing enriched data with created metrics via PySpark  │
│ and loading into local and S3 in Parquet Format         │
│ (Partitioned by Month & Store for optimized scanning by │
│     downstream analytics team )                         │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Deleting local files                                    │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Update status in staging tables of success in MySQL DB  │
│ for all the files                                       │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Checking Spark UI for the jobs on localhost             │
└─────────────────────────────────────────────────────────┘
```
## Spark Job Image
![Alt text](https://github.com/prashant-newway/Etl-data-pipeline-pyspark-aws/blob/main/spark%20jobs%20screenshot.png?raw=true)




## Technical Skills & Features Demonstrated

- **Full ETL Architecture:** Designed a complete ETL pipeline that extracts customer transaction data from AWS S3, transforms it using PySpark, and loads it into a MySQL database for further analysis.
- **Big Data Processing:** Utilized Apache Spark (DataFrames, joins, partitioning) to process high-volume, daily transactional data, improving performance for downstream users.
- **Data Modeling:** Implemented a star schema design with one fact table (customer transactions) and four dimension tables (customer, item, employee, store) to optimize data structure for analytics.
- **Advanced Processing & Performance Optimization:** Leveraged Spark’s capabilities, including partitioning, columnar data formats (Parquet), and optimized storage with partitioned Parquet files (by month and store location) to ensure efficient querying.
- **Cloud Integration & Storage Optimization:** Seamlessly integrated with AWS S3 using the `boto3` SDK for data ingestion and storage, ensuring efficient, scalable data pipelines.
- **Security & Credential Management:** Applied data encryption, secure access key handling, and best practices for credential management to maintain data integrity and privacy.
- **Database Integration & Monitoring:** Integrated MySQL using JDBC connectors, tracked pipeline status through staging tables, and monitored processes via the Spark UI.
- **Data Quality & Validation:** Incorporated schema validation, data quality checks, and handled anomalies such as missing or extra data fields to ensure clean and accurate datasets.
- **Error Handling & Logging:** Developed robust error handling, including exception management, error file management, and detailed logging for better traceability.
- **Production Readiness:** Designed with production-ready features, including dynamic libraries, detailed logging, and process monitoring via staging tables, ensuring stability and maintainability.



## Known Limitations and Future Enhancements possible :

- Workflow Orchestration: Integrate Apache Airflow or AWS-native services for robust scheduling and orchestration of data pipelines.
- Cloud-Native Processing: Eliminate dependency on local environments by enabling direct data processing from AWS S3 with PySpark and MySQL, instead of downloading and processing files locally.
- CI/CD and Automation: Implement CI/CD pipelines for automated testing, deployment, and routine backups, including cleanup of outdated files — currently handled manually.
- Scalability and Flexibility: Enhance support for dynamic bucket names, evolving schemas (e.g. missing or extra columns), and a wider variety of file formats.
- Security and Compliance: Add encryption for personal user data and improve logging with structured JSON output.

## Business Context
The primary business goal is to:
- Track customer spending behavior and generate insights
- Identify and incentivize top-performing sales personnel
- Enable daily/monthly reporting on sales performance
- Create a foundation for targeted customer promotions based on spending patterns

## Setup and Requirements

### Prerequisites

- Python 
- AWS boto3
- OpenJDK 11 , Java , JDBC driver
- MySQL Server 
- Apache Spark

### Database Setup

1. Create MySQL database: `CREATE DATABASE mysql_aws_pyspark_db;`
2. Execute SQL scripts in `sql/table_schemas.sql` to create tables

### Environment Setup

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure environment variables for MySQL connection
5. Set up AWS IAM user with S3 access and obtain access keys
6. Run encryption script to secure your AWS credentials

### Database Setup

1. Create MySQL database: `CREATE DATABASE mysql_aws_pyspark_db;`
2. Execute SQL scripts in `sql/table_schemas.sql` to create tables
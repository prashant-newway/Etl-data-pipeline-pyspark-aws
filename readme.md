# Overview

This is a ETL Data Pipeline that downloads user transaction and profile data from aws s3 -> to local my sql database server -> 

It handles large volumes of data (~15GB/day), includes data encryption, logging, schema validation, AWS S3 integration using Boto3, and is designed with Spark fundamentals for transformation.

Although developed locally for demonstration purposes, this codebase is structured and production-ready. The project mimics daily professional tasks of a DE team, particularly managing transactional and customer sales data, transforming it, and loading it into data marts for further analytics.

# Project Directory Tree

```
.
├── directory_tree.txt
├── local_project_directory_download_location
│   ├── customer_data_mart
│   ├── error_files
│   ├── file_from_s3
│   ├── transactions_partition_data
│   └── transactions_team_data_mart
├── mysql_local_db_tables.png
├── random_generated_data
│   ├── sales_data.csv
│   └── transactions_data.csv
├── readme.md
├── resources
│   ├── dev
│   │   ├── config.py
│   │   └── requirements.txt
│   └── sql_scripts
│       └── table_scripts.sql
├── spark jobs screenshot.png
└── src
    ├── main
    │   ├── delete
    │   │   ├── aws_delete.py
    │   │   ├── database_delete.py
    │   │   └── local_file_delete.py
    │   ├── download
    │   │   └── download_from_s3.py
    │   ├── move
    │   │   └── move_files.py
    │   ├── read
    │   │   ├── database_read.py
    │   │   └── read_from_s3.py
    │   ├── transformations
    │   │   └── jobs
    │   │       ├── customer_mart_sql_tranform_write.py
    │   │       ├── dimension_tables_join.py
    │   │       ├── main.py
    │   │       └── transactions_mart_sql_transform_write.py
    │   ├── upload
    │   │   └── upload_to_s3.py
    │   ├── utility
    │   │   ├── encrypt_decrypt.py
    │   │   ├── logging_config.py
    │   │   ├── mysql_session.py
    │   │   ├── s3_client_object.py
    │   │   └── spark_session.py
    │   └── write
    │       ├── database_write.py
    │       └── dataframe_writer.py
    └── test
        ├── generate_csv_data.py
        ├── generate_customer_table_data.py
        └── transactions_data_upload_s3.py

```

# Project Architecture


```

[Data Generator] 
     ↓
[Local CSV Directory]
     ↓
[Encryption & Boto3 Upload to S3]
     ↓
[S3 Bucket]
     ↓
[Download to Local (temp)]
     ↓
[Spark Processing]
     ↓
[MySQL DB] ↔ [Fact & Dim Tables Join]
     ↓
[Data Marts in Parquet Format (Partitioned by Month & Store ID)]
     ↓
[S3 (Final Data Mart Upload)]

```

# Database ER Diagram


          +-------------------+
          |   Customer_Dim    |
          +-------------------+
          | customer_id (PK)  |
          | name              |
          | join_date         |
          +-------------------+
                    |
                    |
                    v
          +-------------------+
          |    Fact_Table     |
          +-------------------+
          | transaction_id    |
          | customer_id (FK)  |
          | store_id (FK)     |
          | product_id (FK)   |
          | billing_id (FK)   |
          | sales_date        |
          | price, cost       |
          +-------------------+
         /     |        |        \
        v      v        v         v
+------------+ +------------+ +--------------+ +------------------+
| Store_Dim  | | Product_Dim| | Billing_Dim  | | Customer_Mart    |
+------------+ +------------+ +--------------+ +------------------+
| store_id   | | product_id | | billing_id   | | customer_id      |
| address    | | name, info | | name, mgr    | | total_monthly_spend |
| manager    | | price      | | address      | | avg_txn_value    |
+------------+ +------------+ +--------------+ +------------------+


#  Known Limitations
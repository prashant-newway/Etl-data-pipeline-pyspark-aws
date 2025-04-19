import mysql.connector

def get_mysql_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@2025",
        database="mysql_aws_pyspark_db"
    )
    return connection

from pyspark.sql.functions import *
from pyspark.sql.window import Window
from resources.dev import config
from src.main.write.database_write import *

def customer_mart_calculation_table_write(final_customer_data_mart_df):
    window = Window.partitionBy("customer_id","transactions_date_month")
    final_customer_data_mart = final_customer_data_mart_df.withColumn("transactions_date_month",
                                           substring(col("transactions_date"),1,7))\
                    .withColumn("total_transactions_every_month_by_each_customer",
                                sum("total_cost").over(window))\
                    .select("customer_id", concat(col("first_name"),lit(" "),col("last_name"))
                            .alias("full_name"),"address","phone_number",
                            "transactions_date_month",
                            col("total_transactions_every_month_by_each_customer").alias("total_transactions"))\
                    .distinct()


    final_customer_data_mart.show()
    #Write the Data into MySQL customers_data_mart table
    db_writer = DatabaseWriter(url=config.url,properties=config.properties)
    db_writer.write_dataframe(final_customer_data_mart,config.customer_data_mart_table)


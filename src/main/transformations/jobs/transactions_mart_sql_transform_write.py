from pyspark.sql.functions import *
from pyspark.sql.window import Window
from resources.dev import config
from src.main.write.database_write import *



# writing into mysql table


def transactions_mart_calculation_table_write(final_transactions_team_data_mart_df):
    window = Window.partitionBy("store_id","transactions_person_id","transactions_month")
    final_transactions_team_data_mart = final_transactions_team_data_mart_df.withColumn("transactions_month",
                                           substring(col("transactions_date"),1,7))\
                    .withColumn("total_transactions_every_month",
                                sum("total_cost").over(window))\
                    .select("store_id","transactions_person_id", concat(col("transactions_person_first_name"),lit(" "),col("transactions_person_last_name"))
                            .alias("full_name"),
                            "transactions_month",
                            "total_transactions_every_month").distinct()
    rank_window = Window.partitionBy("store_id","transactions_month").orderBy(col("total_transactions_every_month").desc())

    final_transactions_team_data_mart_table = final_transactions_team_data_mart.withColumn("rnk",rank().over(rank_window))\
                                                                        .withColumn("incentive",when(col("rnk")==1,col("total_transactions_every_month")*0.01).otherwise(lit(0)))\
                                                                        .withColumn("incentive",round(col("incentive"),2))\
                                                                                    .withColumn("total_transactions",col("total_transactions_every_month")) \
                                                                                    .select("store_id","transactions_person_id","full_name","transactions_month","total_transactions","incentive")

      

    final_transactions_team_data_mart_table.show()
    #Write the Data into MySQL customers_data_mart table
    print("writing the data into transactions team data mart in mysql db")
    db_writer = DatabaseWriter(url=config.url,properties=config.properties)
    db_writer.write_dataframe(final_transactions_team_data_mart_table,config.transactions_team_data_mart_table)
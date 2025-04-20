from pyspark.sql.functions import *
from src.main.utility.logging_config import *
#enriching the data from different table
def dimesions_table_join(final_df_to_process,
                         customer_table_df,store_table_df,transactions_team_table_df):

 

    #But i do not need all the columns so dropping it
    #save the result into s3_customer_df_join
    logger.info("Joining the final_df_to_process with customer_table_df ")
    s3_customer_df_join = final_df_to_process.alias("s3_data") \
        .join(customer_table_df.alias("ct"),
              col("s3_data.customer_id") == col("ct.customer_id"),"inner") \
        .drop("item_name","price","quantity","additional_column",
              "s3_data.customer_id","customer_joining_date")

    s3_customer_df_join.printSchema()


    logger.info("Joining the s3_customer_df_join with store_table_df ")
    s3_customer_store_df_join= s3_customer_df_join.join(store_table_df,
                             store_table_df["id"]==s3_customer_df_join["store_id"],
                             "inner")\
                        .drop("id","store_pincode","store_opening_date","reviews")

 
    logger.info("Joining the s3_customer_store_df_join with transactions_team_table_df ")
    s3_customer_store_transactions_df_join = s3_customer_store_df_join.join(transactions_team_table_df.alias("st"),
                             col("st.id")==s3_customer_store_df_join["transactions_person_id"],
                             "inner")\
                .withColumn("transactions_person_first_name",col("st.first_name"))\
                .withColumn("transactions_person_last_name",col("st.last_name"))\
                .withColumn("transactions_person_address",col("st.address"))\
                .withColumn("transactions_person_pincode",col("st.pincode"))\
                .drop("id","st.first_name","st.last_name","st.address","st.pincode")
    s3_customer_store_transactions_df_join.printSchema()
    
    return s3_customer_store_transactions_df_join



   #step 1 where i am adding customer table
    # final_df_to_process.alias("s3_data") \
    #     .join(customer_table_df.alias("ct"),
    #           col("s3_data.customer_id") == col("ct.customer_id"),"inner") \
    #     .show()

    #step 2 where i am adding store table details
    # s3_customer_df_join.join(store_table_df,
    #                          store_table_df["id"]==s3_customer_df_join["store_id"],
    #                          "inner").show()

    #But i do not need all the columns so dropping it
    #save the result into s3_customer_store_df_join


       #step 3 where i am adding transactions team table details
    # s3_customer_store_df_join.join(transactions_team_table_df,
    #                          transactions_team_table_df["id"]==s3_customer_store_df_join["transactions_person_id"],
    #                          "inner").show()


    #But i do not need all the columns so dropping it
    #save the result into s3_customer_store_transactions_df_join
import csv
import os
import random
from datetime import datetime, timedelta

customer_ids = list(range(1, 21))
store_ids = list(range(121, 124))
product_data = {
    "item1": 212,
    "item2": 50,
    "item3": 20,
    "item4": 52,
    "item5": 110,
    "item6": 1.5,
    "item7": 100,
    "item8": 40
}
transactions_persons = {
    121: [1, 2, 3],
    122: [4, 5, 6],
    123: [7, 8, 9]
}

start_date = datetime(2024, 3, 3)
end_date = datetime(2024, 8, 20)

file_location = "/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws/random_generated_data/"
csv_file_path = os.path.join(file_location, "transactions_data.csv")
with open(csv_file_path, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["customer_id", "store_id", "item_name", "transactions_date", "transactions_person_id", "price", "quantity", "total_cost"])

    for _ in range(5000):
        customer_id = random.choice(customer_ids)
        store_id = random.choice(store_ids)
        product_name = random.choice(list(product_data.keys()))
        transactions_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        transactions_person_id = random.choice(transactions_persons[store_id])
        quantity = random.randint(1, 10)
        price = product_data[product_name]
        total_cost = price * quantity

        csvwriter.writerow([customer_id, store_id, product_name, transactions_date.strftime("%Y-%m-%d"), transactions_person_id, price, quantity, total_cost])

print("CSV file generated successfully.")

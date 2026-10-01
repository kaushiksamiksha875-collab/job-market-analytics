import pandas as pd
import psycopg2
import os

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="job_market_db",
    user="postgres",
password=os.environ.get("POSTGRES_PASSWORD")
)

query = "SELECT * FROM jobs;"

df = pd.read_sql(query, connection)

df.to_csv("data/jobs_clean.csv", index=False)

connection.close()

print("CSV restored!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Column names:")
print(df.columns.tolist())
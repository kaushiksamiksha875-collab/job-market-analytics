import pandas as pd
import psycopg2
import os

# Read cleaned dataset
df = pd.read_csv("data/jobs_clean.csv")

# Connect to PostgreSQL
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="job_market_db",
    user="postgres",
    password=os.environ.get("POSTGRES_PASSWORD")
)

cursor = connection.cursor()

# Insert jobs
insert_query = """
    INSERT INTO jobs (
        job_id,
        company,
        title,
        description,
        salary,
        ctc,
        work_type,
        location,
        start_date,
        deadline,
        posted_at,
        industry,
        role_type,
        is_on_campus,
        is_active,
        company_type,
        ctc_amount,
        job_type
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (job_id) DO NOTHING;
"""

for _, row in df.iterrows():

    def clean(value):
        if pd.isna(value):
            return None
        return value

    cursor.execute(
        insert_query,
        (
            str(row["id"]),
            clean(row["company"]),
            clean(row["title"]),
            clean(row["description"]),
            clean(row["salary"]),
            clean(row["ctc"]),
            clean(row["work_type"]),
            clean(row["location"]),
            clean(row["start_date"]),
            clean(row["deadline"]),
            clean(row["posted_at"]),
            clean(row["industry"]),
            clean(row["role_type"]),
            clean(row["is_on_campus"]),
            clean(row["is_active"]),
            clean(row["company_type"]),
            clean(row["ctc_amount"]),
            clean(row["job_type"])
        )
    )

connection.commit()

cursor.close()
connection.close()

print("Jobs loaded successfully!")
print("CSV rows:", len(df))
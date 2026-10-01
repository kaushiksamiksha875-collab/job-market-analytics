import json
import hashlib
import psycopg2
import os


# Read scraped live jobs
with open("data/hopin_live_jobs.json", "r", encoding="utf-8") as file:
    jobs = json.load(file)


# Connect to your existing database
# Use the SAME connection details as load_jobs_to_db.py
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="job_market_db",
    user="postgres",
    password=os.environ.get("POSTGRES_PASSWORD")
)

cursor = connection.cursor()


inserted = 0


for job in jobs:

    job_url = job.get("job_url", "")

    # Create a stable ID from the job URL
    job_id = hashlib.md5(
        job_url.encode("utf-8")
    ).hexdigest()

    cursor.execute(
        """
        INSERT INTO live_jobs
        (
            job_id,
            company,
            title,
            description,
            date_posted,
            employment_type,
            job_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (job_id)
        DO UPDATE SET
            company = EXCLUDED.company,
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            date_posted = EXCLUDED.date_posted,
            employment_type = EXCLUDED.employment_type,
            job_url = EXCLUDED.job_url,
            fetched_at = CURRENT_TIMESTAMP;
        """,
        (
            job_id,
            job.get("company"),
            job.get("title"),
            job.get("description"),
            job.get("date_posted"),
            job.get("employment_type"),
            job_url
        )
    )

    inserted += 1


connection.commit()

cursor.close()
connection.close()


print("Live jobs processed:", inserted)
print("Database update complete.")
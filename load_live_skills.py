import re
import psycopg2
import os


skills = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b",
    "Excel": r"\bexcel\b",
    "Power BI": r"\bpower\s*bi\b|\bpowerbi\b",
    "Tableau": r"\btableau\b",
    "Java": r"\bjava\b",
    "JavaScript": r"\bjavascript\b|\bjs\b",
    "C++": r"\bc\+\+\b",
    "C#": r"\bc#\b|\bc\s*sharp\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "Azure": r"\bazure\b",
    "Machine Learning": r"\bmachine learning\b|\bml\b",
    "Artificial Intelligence": r"\bartificial intelligence\b|\bai\b",
    "Generative AI": r"\bgenerative ai\b|\bgenerative artificial intelligence\b|\bgenai\b|\bgen ai\b",
    "LLM": r"\bllm\b|\bllms\b|\blarge language models?\b",
    "Deep Learning": r"\bdeep learning\b",
    "NLP": r"\bnatural language processing\b|\bnlp\b",
    "Data Analysis": r"\bdata analysis\b|\bdata analytics\b",
    "Communication": r"\bcommunication skills?\b|\bstrong communication\b",
    "Leadership": r"\bleadership\b|\bleadership skills?\b",
    "Sales": r"\bsales\b",
    "Marketing": r"\bmarketing\b",
}


connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="job_market_db",
    user="postgres",
password=os.environ.get("POSTGRES_PASSWORD")
)

cursor = connection.cursor()


cursor.execute("""
    SELECT job_id, title, description
    FROM live_jobs;
""")

jobs = cursor.fetchall()

inserted = 0


for job_id, title, description in jobs:

    text = (
        str(title or "") + " " +
        str(description or "")
    ).lower()

    for skill, pattern in skills.items():

        if re.search(pattern, text):

            cursor.execute(
                """
                INSERT INTO live_job_skills
                (job_id, skill)
                VALUES (%s, %s)
                """,
                (job_id, skill)
            )

            inserted += 1


connection.commit()

cursor.close()
connection.close()


print("Live skill records inserted:", inserted)
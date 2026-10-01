import pandas as pd
import psycopg2
import re
import os

# Read cleaned jobs
df = pd.read_csv("data/jobs_clean.csv")

# Skills we want to track
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

# Text fields used for skill detection
text_columns = [
    "title",
    "description",
    "preferred_qualifications",
    "linkedin_post_text"
]

available_columns = [col for col in text_columns if col in df.columns]

df["job_text"] = (
    df[available_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.lower()
)

# Connect to PostgreSQL
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="job_market_db",
    user="postgres",
password=os.environ.get("POSTGRES_PASSWORD")
)

cursor = connection.cursor()

insert_query = """
    INSERT INTO job_skills (job_id, skill)
    VALUES (%s, %s);
"""

skill_record_count = 0

for _, row in df.iterrows():

    job_id = str(row["id"])
    text = row["job_text"]

    for skill, pattern in skills.items():

        if re.search(pattern, text):
            cursor.execute(
                insert_query,
                (job_id, skill)
            )

            skill_record_count += 1

connection.commit()

cursor.close()
connection.close()

print("Skills loaded successfully!")
print("Skill records inserted:", skill_record_count)
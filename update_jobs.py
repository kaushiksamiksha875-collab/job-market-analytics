import requests
from bs4 import BeautifulSoup
import json
import time
import hashlib
import re
import psycopg2
import os


# =========================================================
# 1. SETTINGS
# =========================================================

URL = "https://hopinjobs.com/off-campus-drive-2026"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =========================================================
# 2. SKILLS TO DETECT
# =========================================================

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


# =========================================================
# 3. SCRAPE HOPIN
# =========================================================

print("Starting Hopin scraper...")

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

print("Main page status:", response.status_code)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)


# Find job links
links = soup.find_all("a", href=True)

job_links = []

for link in links:

    href = link["href"]

    if "/jobs/" in href:

        if href.startswith("/"):
            href = "https://hopinjobs.com" + href

        if href not in job_links:
            job_links.append(href)


print("Job links found:", len(job_links))


# =========================================================
# 4. COLLECT JOB DATA
# =========================================================

jobs = []

for number, job_url in enumerate(job_links, start=1):

    print(
        f"Fetching job {number}/{len(job_links)}"
    )

    try:

        job_response = requests.get(
            job_url,
            headers=HEADERS,
            timeout=30
        )

        job_soup = BeautifulSoup(
            job_response.text,
            "html.parser"
        )

        json_ld = job_soup.find_all(
            "script",
            type="application/ld+json"
        )

        for block in json_ld:

            try:

                data = json.loads(
                    block.get_text()
                )

                if (
                    isinstance(data, dict)
                    and data.get("@type") == "JobPosting"
                ):

                    job = {
                        "job_url": job_url,
                        "title": data.get("title"),
                        "company": data.get(
                            "hiringOrganization", {}
                        ).get("name"),
                        "description": data.get(
                            "description"
                        ),
                        "date_posted": data.get(
                            "datePosted"
                        ),
                        "employment_type": data.get(
                            "employmentType"
                        )
                    }

                    jobs.append(job)

                    break

            except Exception:
                continue

        time.sleep(0.3)

    except Exception as e:

        print(
            "Error fetching job:",
            e
        )


print(
    "\nJobs collected:",
    len(jobs)
)


# =========================================================
# 5. SAVE JSON
# =========================================================

with open(
    "data/hopin_live_jobs.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        jobs,
        file,
        indent=2,
        ensure_ascii=False
    )


print(
    "Saved JSON successfully."
)


# =========================================================
# 6. CONNECT TO POSTGRESQL
# =========================================================

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="job_market_db",
    user="postgres",
password=os.environ.get("POSTGRES_PASSWORD")
)

cursor = connection.cursor()


# =========================================================
# 7. UPDATE LIVE JOBS
# =========================================================

jobs_processed = 0

for job in jobs:

    job_url = job.get(
        "job_url",
        ""
    )

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
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)

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

    jobs_processed += 1


connection.commit()


print(
    "Live jobs processed:",
    jobs_processed
)


# =========================================================
# 8. REFRESH LIVE SKILLS
# =========================================================

cursor.execute(
    "DELETE FROM live_job_skills;"
)

skill_records = 0


for job in jobs:

    job_url = job.get(
        "job_url",
        ""
    )

    job_id = hashlib.md5(
        job_url.encode("utf-8")
    ).hexdigest()

    text = (
        str(job.get("title") or "")
        + " "
        + str(job.get("description") or "")
    ).lower()

    for skill, pattern in skills.items():

        if re.search(
            pattern,
            text
        ):

            cursor.execute(
                """
                INSERT INTO live_job_skills
                (
                    job_id,
                    skill
                )
                VALUES
                (%s, %s)
                """,
                (
                    job_id,
                    skill
                )
            )

            skill_records += 1


connection.commit()


# =========================================================
# 9. CLOSE DATABASE
# =========================================================

cursor.close()

connection.close()


print(
    "Live skill records:",
    skill_records
)

print(
    "\n================================"
)

print(
    "LIVE PIPELINE COMPLETE"
)

print(
    "================================"
)
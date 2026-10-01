import pandas as pd

df = pd.read_csv("data/jobs_clean.csv")

print("Rows:", len(df))
print("Columns:")
print(df.columns.tolist())
print("\nMissing values:")
print(df.isnull().sum())
df.duplicated(subset="job_id").sum()
# Remove columns we don't need for analysis
df = df.drop(columns=["logo"], errors="ignore")

# Save cleaned dataset
df.to_csv("data/jobs_clean.csv", index=False)

print("\nClean dataset saved!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nAll columns:")

for column in df.columns:
    print(column)


for i in range(3):
    print("\n--- Job", i + 1, "---")

    print("\nTop job roles:")

    print(df["role_type"].value_counts().head(20))

    # -----------------------------
    # Skill Demand Analysis
    # -----------------------------

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

    import re

    # Combine useful text fields
    text_columns = [
        "title",
        "description",

    ]

    available_columns = [col for col in text_columns if col in df.columns]

    df["job_text"] = (
        df[available_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )

    skill_counts = {}

    for skill, pattern in skills.items():
        skill_counts[skill] = df["job_text"].str.contains(
            pattern,
            regex=True,
            na=False
        ).sum()

    skill_results = (
        pd.Series(skill_counts)
        .sort_values(ascending=False)
    )

    print("\nTop demanded skills:")

    print(skill_results.head(20))
    skill_percentage = (skill_results / len(df)) * 100

    print("\nSkill demand percentage:")

    print(skill_percentage.head(20).round(2))
    print("\nRole types:")
    print(df["role_type"].value_counts())

    # -----------------------------
    # Skill demand by role
    # -----------------------------

    print("\nTop skills by major role:")

    major_roles = [
        "Sales",
        "Human Resources",
        "Business Development",
        "Software Engineering",
        "Operations"
    ]

    for role in major_roles:
        role_df = df[df["role_type"] == role]

        if len(role_df) == 0:
            continue

        role_counts = {}

        for skill, pattern in skills.items():
            role_counts[skill] = role_df["job_text"].str.contains(
                pattern,
                regex=True,
                na=False
            ).sum()

        role_results = pd.Series(role_counts).sort_values(
            ascending=False
        )

        print(f"\n--- {role} ({len(role_df)} jobs) ---")
        print(role_results.head(10))
        # -----------------------------
        # Location Analysis
        # -----------------------------

        print("\nTop job locations:")

        location_counts = (
            df["location"]
            .fillna("Unknown")
            .value_counts()
        )

        print(location_counts.head(20))# -----------------------------
# Clean location names
# -----------------------------

def clean_location(location):
    location = str(location).strip().lower()

    if "bengaluru" in location or "bangalore" in location:
        return "Bengaluru"
    elif "mumbai" in location:
        return "Mumbai"
    elif "delhi" in location:
        return "Delhi"
    elif "pune" in location:
        return "Pune"
    elif "hyderabad" in location:
        return "Hyderabad"
    elif "chennai" in location:
        return "Chennai"
    elif "ahmedabad" in location:
        return "Ahmedabad"
    elif "kolkata" in location:
        return "Kolkata"
    elif "noida" in location:
        return "Noida"
    elif "gurugram" in location or "gurgaon" in location:
        return "Gurugram"
    else:
        return location.title()


df["clean_city"] = df["location"].apply(clean_location)

print("\nCleaned city demand:")

print(df["clean_city"].value_counts().head(15))

# -----------------------------
# AI & Emerging Skills Analysis
# -----------------------------

ai_skills = [
    "Artificial Intelligence",
    "Generative AI",
    "LLM",
    "Machine Learning",
    "Deep Learning",
    "NLP"
]

ai_counts = skill_results.reindex(ai_skills).fillna(0).astype(int)

ai_percentage = (ai_counts / len(df)) * 100

ai_analysis = pd.DataFrame({
    "Job_Postings": ai_counts,
    "Demand_Percentage": ai_percentage.round(2)
})

print("\nAI & Emerging Skills Analysis:")

print(ai_analysis)
print("CSV columns:")
print(pd.read_csv("data/jobs_clean.csv").columns.tolist())

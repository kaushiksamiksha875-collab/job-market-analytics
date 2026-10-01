import requests
import json

url = "https://api.hopinjobs.com/api/jobs?is_unofficial=true"

response = requests.get(url)

print("Status:", response.status_code)

data = response.json()

with open("data/jobs_raw.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Number of jobs:", len(data["jobs"]))
print("Data saved successfully!")
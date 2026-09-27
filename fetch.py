"""Collects UK data jobs from the Adzuna API into data/jobs.json and data/history.json.
Stdlib only. Runs daily on GitHub Actions; run locally with:
  ADZUNA_ID=... ADZUNA_KEY=... python3 fetch.py
"""
import datetime as dt
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROLES = {"Data Scientist": "data scientist", "Data Analyst": "data analyst",
         "Data Engineer": "data engineer", "ML Engineer": "machine learning engineer"}
PAGES = 5            # 50 ads per page -> up to 250 per role per day (20 API calls; free tier allows 250/day)
KEEP_DAYS = 90       # how long an ad stays in the dataset

SKILLS = {  # name -> regex (case-insensitive unless noted)
    "Python": r"\bpython\b", "SQL": r"\bsql\b", "R": r"(?-i:\bR\b)(?![&/])", "Excel": r"\bexcel\b",
    "Power BI": r"\bpower ?bi\b", "Tableau": r"\btableau\b", "Looker": r"\blooker\b",
    "AWS": r"\baws\b|amazon web services", "Azure": r"\bazure\b", "GCP": r"\bgcp\b|google cloud",
    "Spark": r"\b(py)?spark\b", "Databricks": r"\bdatabricks\b", "Snowflake": r"\bsnowflake\b",
    "dbt": r"\bdbt\b", "Airflow": r"\bairflow\b", "Kafka": r"\bkafka\b", "ETL": r"\betl\b|\belt\b",
    "Pandas": r"\bpandas\b", "scikit-learn": r"scikit|sklearn", "TensorFlow": r"tensorflow",
    "PyTorch": r"pytorch", "Machine learning": r"machine learning|\bml\b",
    "Deep learning": r"deep learning", "NLP": r"\bnlp\b|natural language",
    "GenAI / LLMs": r"\bllms?\b|generative ai|gen ?ai|large language", "Statistics": r"statistic",
    "A/B testing": r"a/b test|experimentation", "Docker": r"docker", "Kubernetes": r"kubernetes|\bk8s\b",
    "Git": r"\bgit(hub|lab)?\b", "SAS": r"\bsas\b", "Java": r"\bjava\b", "Scala": r"\bscala\b",
}
SKILL_RE = {k: re.compile(v, re.I) for k, v in SKILLS.items()}


def fetch_page(role_query, page):
    params = urllib.parse.urlencode({
        "app_id": os.environ["ADZUNA_ID"], "app_key": os.environ["ADZUNA_KEY"],
        "what_phrase": role_query, "results_per_page": 50, "sort_by": "date",
        "max_days_old": 30, "content-type": "application/json"})
    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}?{params}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["results"]


def clean(ad, role):
    text = re.sub(r"<[^>]+>", " ", f"{ad.get('title', '')} {ad.get('description', '')}")
    area = ad.get("location", {}).get("area", [])
    real_salary = str(ad.get("salary_is_predicted", "1")) == "0" and ad.get("salary_min")
    return {
        "id": str(ad["id"]),
        "title": ad.get("title", "").strip(),
        "company": ad.get("company", {}).get("display_name", "Unknown").strip(),
        "region": area[1] if len(area) > 1 else "UK",
        "place": ad.get("location", {}).get("display_name", ""),
        "role": role,
        "salary": round((ad["salary_min"] + ad.get("salary_max", ad["salary_min"])) / 2) if real_salary else None,
        "posted": ad.get("created", "")[:10],
        "remote": bool(re.search(r"\bremote\b|\bhybrid\b|work from home", text, re.I)),
        "skills": [k for k, rx in SKILL_RE.items() if rx.search(text)],
        "url": ad.get("redirect_url", ""),
    }


def update(jobs, history, fetched, today):
    """Merge newly fetched ads, drop old ones, record today's snapshot. Pure function (tested)."""
    by_id = {j["id"]: j for j in jobs}
    by_id.update({j["id"]: j for j in fetched})
    cutoff = (dt.date.fromisoformat(today) - dt.timedelta(days=KEEP_DAYS)).isoformat()
    jobs = sorted((j for j in by_id.values() if j["posted"] >= cutoff), key=lambda j: j["posted"], reverse=True)
    history = [h for h in history if h["date"] != today] + [{
        "date": today, "live_ads": len(fetched),
        "by_role": {r: sum(j["role"] == r for j in fetched) for r in ROLES}}]
    return jobs, history


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


if __name__ == "__main__":
    fetched = {}
    for role, query in ROLES.items():
        for page in range(1, PAGES + 1):
            results = fetch_page(query, page)
            for ad in results:
                fetched.setdefault(str(ad["id"]), clean(ad, role))
            print(f"{role} page {page}: {len(results)} ads")
            if len(results) < 50:
                break
            time.sleep(1)                                 # be polite to the API
    jobs, history = update(load("data/jobs.json", []), load("data/history.json", []),
                           list(fetched.values()), dt.date.today().isoformat())
    with open("data/jobs.json", "w") as f:
        json.dump(jobs, f, separators=(",", ":"))
    with open("data/history.json", "w") as f:
        json.dump(history, f, indent=1)
    print(f"{len(fetched)} ads fetched today, {len(jobs)} in dataset")

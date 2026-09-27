from fetch import clean, update

ad = {"id": 1, "title": "Senior Data Scientist (Hybrid)", "company": {"display_name": "Acme"},
      "location": {"area": ["UK", "Wales", "Cardiff"], "display_name": "Cardiff, Wales"},
      "description": "Python, SQL and R required. Power BI a plus. R&D team. Build ML models on AWS.",
      "salary_min": 50000, "salary_max": 60000, "salary_is_predicted": "0", "created": "2026-09-20T10:00:00Z",
      "redirect_url": "https://x"}
j = clean(ad, "Data Scientist")
assert j["region"] == "Wales" and j["salary"] == 55000 and j["remote"] and j["posted"] == "2026-09-20", j
assert set(j["skills"]) >= {"Python", "SQL", "R", "Power BI", "AWS", "Machine learning"}, j["skills"]
assert "Excel" not in j["skills"]
assert clean({**ad, "salary_is_predicted": "1"}, "x")["salary"] is None   # Adzuna's guesses are ignored
assert "R" not in clean({**ad, "description": "Our R&D team"}, "x")["skills"]

old = {**j, "id": "old", "posted": "2026-01-01"}
jobs, hist = update([old, j], [{"date": "2026-09-27", "live_ads": 9, "by_role": {}}], [j], "2026-09-27")
assert [x["id"] for x in jobs] == ["1"]              # >90-day-old ad dropped, no duplicates
assert len(hist) == 1 and hist[0]["live_ads"] == 1   # re-running the same day replaces the snapshot
print("ok")

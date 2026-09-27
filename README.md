# UK Data Jobs Market

**Live dashboard:** https://adityavdn.github.io/uk-data-jobs/

A live picture of the UK market for data scientists, data analysts, data engineers and ML engineers:
which skills employers want, what they pay in each region, who's hiring, and how demand changes over time.

- **Pipeline:** `fetch.py` pulls fresh job ads from the Adzuna API every day. It runs on GitHub Actions, so there's no server.
  It cleans the ads, removes duplicates, pulls out ~30 skills with regular expressions, and keeps 90 days of history.
- **Dashboard:** `index.html` is a single static page. Filtering by role, region, skill or keyword updates every chart.
- **Honest numbers:** salary stats use only salaries employers actually stated, not Adzuna's estimates.

Run it locally: `ADZUNA_ID=... ADZUNA_KEY=... python3 fetch.py`, then `python3 -m http.server` and open http://localhost:8000.
Run the tests with `python3 test_fetch.py`.

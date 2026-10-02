# UK Data Jobs Market

A live dashboard of the UK data science job market, showing skills demand, salaries by region and hiring trends.

## Overview

This project tracks the UK market for data scientists, data analysts, data engineers and machine learning engineers. It brings together job-ad data, salary information and skill demand signals in a single interactive dashboard.

## Pipeline

- `fetch.py` pulls job advertisements from the Adzuna API.
- GitHub Actions runs the fetch process automatically.
- The data is cleaned and deduplicated before being stored as historical records.
- A set of text-processing rules extracts relevant skills and salary signals.

## Dashboard

The front end is a static HTML dashboard with filters for:

- role
- region
- skill
- keyword

It updates dynamically and presents market trends in a visual format.

## Tech Stack

- Python
- JavaScript
- HTML
- GitHub Actions
- Adzuna API

## How to run

```bash
ADZUNA_ID=... ADZUNA_KEY=... python3 fetch.py
python3 -m http.server
```

Then open the local dashboard in a browser.

## Project structure

```text
.
├── fetch.py
├── test_fetch.py
├── index.html
├── README.md
└── data or generated output files
```


# US-Visa-Data-Archive

This project converts monthly U.S. Department of State visa issuance PDFs into a structured dataset for analysis and dashboarding.

## What it does

- Scrapes immigrant and nonimmigrant visa PDF links from the official State Department pages
- Downloads new PDFs
- Extracts tabular data from each file
- Standardizes country names
- Parses month/year fields
- Enriches visa classes using a reference codebook
- Merges with existing processed data and re-aggregates to prevent duplicate inflation
- Tracks processed source files
- Publishes updates through GitHub Actions

## Output

- `data/processed/visa_data.csv`: final longitudinal dataset
- `data/processed/processed_files.json`: source-file state tracker

Main dataset columns include:

- `country`
- `visa_type`
- `visa_program` (`immigrant` or `nonimmigrant`)
- `count`
- `date`, `month`, `year`
- visa metadata from `data/reference/visa_codebook.csv` (for example: `program_type`, `eligibility_pathway`, `visa_description`)

## Project structure

```text
.
├── build_visa_dataset.py
├── requirements.txt
├── src/
│   ├── scrape.py
│   ├── extract.py
│   ├── transform.py
│   └── tracker.py
├── data/
│   ├── raw/
│   ├── reference/
│   │   └── visa_codebook.csv
│   └── processed/
│       ├── visa_data.csv
│       └── processed_files.json
└── .github/workflows/
    └── monthly_update.yml
```

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python build_visa_dataset.py
```

## Automation

GitHub Actions workflow: `.github/workflows/monthly_update.yml`

- Scheduled run: day 1 of each month at `05:00 UTC`
- Manual trigger: `workflow_dispatch`
- Executes `python build_visa_dataset.py`
- Commits updated `data/processed/visa_data.csv` and `data/processed/processed_files.json` back to the repository when changes exist

For automated commits, repository Actions permissions must allow write access to contents.

## Data integrity behavior

- Fails if visa codebook has duplicate `visa_type + visa_program` keys
- Fails if extracted rows contain unmapped visa classes (writes `data/processed/unknown_visa_types.csv` for inspection)
- Requires valid extractable rows per processed PDF in strict mode
- Re-aggregates by business key (`date`, `visa_program`, `country`, `visa_type`) to avoid duplicate count inflation

## Data sources

- [Monthly Immigrant Visa Issuances](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/immigrant-visa-statistics/monthly-immigrant-visa-issuances.html)
- [Monthly Nonimmigrant Visa Issuances](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/nonimmigrant-visa-statistics/monthly-nonimmigrant-visa-issuances.html)

Visa codebook reference was manually compiled from State Department visa classification resources [1](https://fam.state.gov/FAM/09FAM/09FAM050201.html) and [2](https://fam.state.gov/FAM/09FAM/09FAM040201.html).

## Why this exists

The State Department publishes high-value visa statistics mostly as PDFs.  
This project provides a reproducible pipeline to keep those data in analysis-ready CSV form.

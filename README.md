# US-Visa-Data-Archive

This project converts monthly U.S. Department of State visa issuance reports (published as PDFs) into a clean, structured, and continuously updated dataset suitable for research and dashboarding.

It automatically:

- Scrapes new immigrant and nonimmigrant visa issuance PDFs

- Extracts tables from PDF format

- Standardizes country names

- Parses dates

- Merges visa metadata from a reference codebook

- Appends new data incrementally

- Tracks processed files to avoid duplication

- Runs automatically via GitHub Actions

📦 What This Project Produces

data/processed/visa_data.csv

A longitudinal dataset containing:

Country

Visa type

Visa program (immigrant / nonimmigrant)

Year

Month

Issuance count

Program category

Eligibility pathway

Visa description

Designed for:

Tableau dashboards

Research analysis

Visual essays

Public policy data exploration

🏗 Project Structure
us-visa-data-builder/
│
├── run_pipeline.py
│
├── src/
│   ├── scrape.py        # Finds and downloads new PDFs
│   ├── extract.py       # Extracts tables from PDFs
│   ├── transform.py     # Standardizes countries, dates, visa metadata
│   └── tracker.py       # Tracks processed files
│
├── data/
│   ├── raw/             # (temporary PDFs if needed)
│   ├── reference/
│   │   └── visa_codebook.csv
│   └── processed/
│       ├── visa_data.csv
│       └── processed_files.json
│
└── .github/workflows/
    └── monthly_update.yml
▶️ Running the Pipeline Locally

Install dependencies:

pip install requests beautifulsoup4 pdfplumber pandas

Run:

python run_pipeline.py

The pipeline will:

Detect new PDF files

Process only new files

Append data to the existing dataset

Update the processed file tracker

🔁 Automation

This project uses GitHub Actions.

The workflow:

Runs automatically on the 1st of each month

Can also be triggered manually

Executes the pipeline

Commits updated data back to the repository

Workflow file:

.github/workflows/monthly_update.yml

To enable automated commits:

Go to:

Settings → Actions → General → Workflow permissions

Enable:

Read and write permissions

🔐 Data Integrity

The pipeline:

Fails if unknown visa types are detected

Fails if duplicate visa metadata keys exist

Prevents re-processing of already ingested files

Ensures visa_type + migration_type are unique merge keys

This prevents silent data corruption.

📚 Data Sources

U.S. Department of State:

Immigrant Visa Issuances (Monthly)

Nonimmigrant Visa Issuances (Monthly)

All source data originates from publicly available government publications.

🧠 Why This Exists

Government data is often published in static PDF tables.

This project transforms those static reports into:

A structured dataset

A research-ready format

A continuously updated data archive

It bridges the gap between government reporting and analytical infrastructure.

📌 Future Extensions

Possible enhancements:

Historical backfill validation

Logging & error reporting

Dashboard auto-refresh integration

Data quality checks

Deployment to a public API

If you want, I can now:

Make a slightly more public-facing version

Make a more technical version

Or tailor it specifically for your portfolio site

Just tell me the audience.

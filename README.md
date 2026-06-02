# US Visa Data Archive

An interactive dashboard and open dataset tracking US visa issuance by applicant's country of birth and visa class, from 2017 to the present. Data is sourced directly from the US Department of State monthly reports and updated automatically each month.

**[View the live dashboard](https://shadi-sadie.github.io/US-Visa-Data-Archive/visa_dashboard.html)**

---

## What you can explore

The dashboard covers immigrant and nonimmigrant visas broken down by applicant's country of birth across 204 countries and territories, spanning 257 distinct visa types grouped into meaningful categories. Note: the data reflects country of birth, not the consulate or post where the visa was issued.

**Overview**
See global issuance totals for any year, mapped by country. Switch between absolute counts and per-100K population to compare countries of vastly different sizes. A ranked list of the top 10 nationalities updates with every filter change.

**Trends**
Track how visa issuance has changed year over year from 2017 through the present. Drill into specific program types such as Temporary Worker, Study and Exchange, Family-based, or Employment-based to see how individual categories have evolved over time. Annotated markers highlight known policy events, travel bans, and embassy closures that caused visible shifts in the data.

**Country detail**
Select any country to see its full visa history: total issuance by year, a breakdown of visa categories as a donut chart, rank among all countries, and year-over-year change. A timeline chart shows the full arc from 2017 to today.

**Compare**
Place up to five countries side by side to compare absolute issuance or per-100K rates for any given year.

---

## Data scope and coverage

| | |
|---|---|
| Source | US Department of State monthly PDF reports |
| Coverage | January 2017 to present |
| Countries (by birth) | 204 countries and territories |
| Visa types | 257 types across immigrant and nonimmigrant programs |
| Update cadence | Automatically updated on the 1st of each month |

### Important limitations

**Visa Waiver Program countries are underrepresented.** Citizens of the 42 VWP countries (including the UK, Germany, France, Japan, South Korea, and most of Western Europe) can enter the US for tourism or business for up to 90 days via ESTA without a visa. Those entries are not captured here. This means VWP countries will appear smaller than non-VWP countries like India or Mexico even when overall travel volumes are comparable. Canadian citizens are similarly exempt from tourist and business visas.

**Visa numbers reflect policy, not just demand.** Sudden drops for specific countries in specific years often reflect executive orders, travel bans, embassy closures, or bilateral consular restrictions rather than changes in travel interest. The Country view marks known events directly on the timeline.

---

## Project structure

```
.
├── build_visa_dataset.py       # Main pipeline: scrape, extract, transform
├── build_visualization.py      # Builds visa_aggregated.json from processed CSV
├── requirements.txt
├── src/
│   ├── scrape.py
│   ├── extract.py
│   ├── transform.py
│   └── tracker.py
├── data/
│   ├── raw/                    # Downloaded PDFs
│   ├── reference/
│   │   └── visa_codebook.csv   # Visa type to category mappings
│   └── processed/
│       ├── visa_data.csv
│       └── processed_files.json
├── docs/
│   ├── visa_dashboard.html     # Interactive dashboard (served via GitHub Pages)
│   └── visa_aggregated.json    # Pre-aggregated JSON loaded by the dashboard
└── .github/workflows/
    └── monthly_update.yml
```

---

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the data pipeline:

```bash
python build_visa_dataset.py
```

Rebuild the visualization data after any pipeline run:

```bash
python build_visualization.py
```

Serve the dashboard locally:

```bash
python -m http.server 8765 --directory docs
```

Then open `http://localhost:8765/visa_dashboard.html` in your browser.

---

## Automation

The GitHub Actions workflow at `.github/workflows/monthly_update.yml` runs on the 1st of each month at 05:00 UTC. It can also be triggered manually from the Actions tab.

Each run:
1. Scrapes the State Department website for new PDF links
2. Downloads and parses any PDFs not yet in the archive
3. Rebuilds `visa_data.csv`
4. Rebuilds `visa_aggregated.json` for the dashboard
5. Commits and pushes all changed files back to the repository

If the State Department publishes data mid-month (which is typical), the next scheduled run or a manual trigger will pick it up.

---

## Data integrity

The pipeline enforces several checks at each run:

- Fails if `visa_codebook.csv` contains duplicate `visa_type + visa_program` keys
- Writes `data/processed/unknown_visa_types.csv` and exits with an error if any extracted visa types are not present in the codebook, so that new visa types introduced by the State Department are caught and categorized before the data goes live
- Re-aggregates by business key (`date`, `visa_program`, `country`, `visa_type`) to prevent duplicate count inflation if a source PDF is processed more than once

---

## Data sources

- [Monthly Immigrant Visa Issuances](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/immigrant-visa-statistics/monthly-immigrant-visa-issuances.html)
- [Monthly Nonimmigrant Visa Issuances](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/nonimmigrant-visa-statistics/monthly-nonimmigrant-visa-issuances.html)

The visa codebook was compiled manually from the State Department's Foreign Affairs Manual, specifically [9 FAM 502](https://fam.state.gov/FAM/09FAM/09FAM050201.html) and [9 FAM 402](https://fam.state.gov/FAM/09FAM/09FAM040201.html).

---

## Why this project exists

The State Department publishes detailed visa statistics every month, but exclusively as PDFs. This makes longitudinal analysis difficult: comparing 2017 to 2024, tracking how a policy change affected a specific country, or simply asking how many student visas were issued last year all require manual work that most people will not do.

This project converts that entire archive into a clean, analysis-ready dataset and keeps it current automatically. The interactive dashboard makes the data accessible without requiring any technical setup.

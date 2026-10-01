# US Visa Data Archive

An interactive dashboard and open dataset tracking US visa issuance by applicant's country of birth and visa class, from 2017 to the present. Data is sourced directly from the US Department of State monthly reports.

**[View the live dashboard](https://shadi-sadie.github.io/US-Visa-Data-Archive/visa_dashboard.html)**

---

## What you can explore

The dashboard covers immigrant and nonimmigrant visas broken down by applicant's country of birth across 204 countries and territories, spanning 237 distinct visa types grouped into meaningful categories. Note: the data reflects country of birth, not the consulate or post where the visa was issued.

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
| Source | US Department of State monthly reports (PDF, and `.xlsx` from FY2026 onward) |
| Coverage | March 2017 through February 2026 |
| Countries (by birth) | 204 countries and territories |
| Visa types | 237 types across immigrant and nonimmigrant programs |
| Update cadence | Manual — see [Automation](#automation) |

### Important limitations

**Visa Waiver Program countries are underrepresented.** Citizens of the 42 VWP countries (including the UK, Germany, France, Japan, South Korea, and most of Western Europe) can enter the US for tourism or business for up to 90 days via ESTA without a visa. Those entries are not captured here. This means VWP countries will appear smaller than non-VWP countries like India or Mexico even when overall travel volumes are comparable. Canadian citizens are similarly exempt from tourist and business visas.

**Visa numbers reflect policy, not just demand.** Sudden drops for specific countries in specific years often reflect executive orders, travel bans, embassy closures, or bilateral consular restrictions rather than changes in travel interest. The Country view marks known events directly on the timeline.

---

## Project structure

```
.
├── build_visa_dataset.py       # Main pipeline: scrape, extract, transform
├── ingest_local.py             # Ingests manually downloaded .xlsx files from data/raw/
├── build_visualization.py      # Builds visa_aggregated.json from processed CSV
├── requirements.txt
├── src/
│   ├── scrape.py
│   ├── extract.py
│   ├── transform.py
│   └── tracker.py
├── data/
│   ├── raw/                    # Source documents (.pdf, and .xlsx from FY2026)
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

Run the data pipeline (scrapes upstream; currently blocked by Cloudflare — see [Automation](#automation)):

```bash
python build_visa_dataset.py
```

Or ingest source files you downloaded by hand into `data/raw/`:

```bash
python ingest_local.py
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

> **Automated collection is currently blocked.** travel.state.gov now sits behind a Cloudflare bot
> challenge that returns `403 Forbidden` to automated clients, so the scheduled workflow can no
> longer fetch new releases. New months must be downloaded by hand — see
> [Updating manually](#updating-manually) below.

The GitHub Actions workflow at `.github/workflows/monthly_update.yml` runs on the 1st of each month at 05:00 UTC. It can also be triggered manually from the Actions tab.

Each run:
1. Scrapes the State Department website for new source links
2. Downloads and parses any files not yet in the archive
3. Rebuilds `visa_data.csv`
4. Rebuilds `visa_aggregated.json` for the dashboard
5. Commits and pushes the updated data files back to the repository

When the upstream site is unreachable, the pipeline retries with backoff and then exits cleanly
rather than failing the job, so a blocked month is a no-op instead of a red build. The practical
consequence is that a persistent block is silent — if the dashboard looks stale, check whether new
months are actually being ingested.

### Updating manually

Because a real browser passes the Cloudflare challenge that automated clients cannot:

1. Open the [immigrant](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/immigrant-visa-statistics/monthly-immigrant-visa-issuances.html)
   and [nonimmigrant](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/nonimmigrant-visa-statistics/monthly-nonimmigrant-visa-issuances.html)
   pages in a browser and clear the challenge.
2. Download any months newer than the latest in `visa_data.csv`. Prefer the `.xlsx` versions —
   they parse far more reliably than the PDF table extraction.
3. Save them into `data/raw/` without renaming; the month and year are parsed from the filename.
4. Run the ingest and rebuild the dashboard data:

```bash
python ingest_local.py
python build_visualization.py
```

`ingest_local.py` skips months already present in the dataset. Pass `--replace` to re-ingest a
month; it replaces rather than appends, so re-running it never double-counts.

---

## Data integrity

The pipeline enforces several checks at each run:

- Fails if `visa_codebook.csv` contains duplicate `visa_type + visa_program` keys
- Writes `data/processed/unknown_visa_types.csv` and prints a warning if any extracted visa types are not present in the codebook, so that new visa types introduced by the State Department are caught and categorized. These rows are still included, with null metadata columns
- Prints a warning for any country name that survives standardization without matching the reference list, so new or renamed source spellings surface rather than silently fragmenting a country's history
- Collapses rows to one per business key (`date`, `visa_program`, `country`, `visa_type`), so country remapping (for example several China spellings folding into one) sums into a single row

Note that this collapse **sums** counts, so ingesting the same month twice would inflate it. Guarding
against that is the job of `processed_files.json`, which records what has already been consumed;
`ingest_local.py` additionally replaces rather than appends any month it re-ingests.

---

## Data sources

- [Monthly Immigrant Visa Issuances](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/immigrant-visa-statistics/monthly-immigrant-visa-issuances.html)
- [Monthly Nonimmigrant Visa Issuances](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/nonimmigrant-visa-statistics/monthly-nonimmigrant-visa-issuances.html)

The visa codebook was compiled manually from the State Department's Foreign Affairs Manual, specifically [9 FAM 502](https://fam.state.gov/FAM/09FAM/09FAM050201.html) and [9 FAM 402](https://fam.state.gov/FAM/09FAM/09FAM040201.html).

---

## Why this project exists

The State Department publishes detailed visa statistics every month, historically as PDFs only (spreadsheets were added alongside them from FY2026). This makes longitudinal analysis difficult: comparing 2017 to 2024, tracking how a policy change affected a specific country, or simply asking how many student visas were issued last year all require manual work that most people will not do.

This project converts that entire archive into a clean, analysis-ready dataset, and preserves the original source documents in `data/raw/` so every figure stays traceable back to the release it came from. The interactive dashboard makes the data accessible without requiring any technical setup.

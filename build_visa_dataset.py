import time

import os
import pandas as pd

from src.scrape import scrape_pdfs
from src.extract import process_pdfs
from src.transform import (
    standardize_countries,
    validate_countries,
    split_date,
    aggregate_business_keys,
    add_visa_metadata,
)
from src.tracker import load_state, save_state


IMMIGRANT_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/immigrant-visa-statistics/monthly-immigrant-visa-issuances.html"

NONIMMIGRANT_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/nonimmigrant-visa-statistics/monthly-nonimmigrant-visa-issuances.html"

OUTPUT_PATH = "data/processed/visa_data.csv"
BASE_COLUMNS = ["date", "visa_program", "country", "visa_type", "count"]


def main():
    start = time.time()

    processed = load_state()

    # --- Scrape links ---
    immigrant_links = scrape_pdfs(IMMIGRANT_URL, ["FSC"])
    nonimmigrant_links = scrape_pdfs(NONIMMIGRANT_URL, ["nationality"])

    all_links = immigrant_links + nonimmigrant_links

    # --- Only process new files ---
    new_links = [l for l in all_links if l not in processed]

    if not new_links:
        print("No new files found.")
        return

    # --- Separate by program ---
    immigrant_new = [l for l in new_links if l in immigrant_links]
    nonimmigrant_new = [l for l in new_links if l in nonimmigrant_links]

    # --- Extract ---
    df_imm = process_pdfs(immigrant_new, "immigrant")
    df_non = process_pdfs(nonimmigrant_new, "nonimmigrant")

    df = pd.concat([df_imm, df_non], ignore_index=True)

    if df.empty:
        print("No data extracted.")
        return

    # --- Transform ---
    df = standardize_countries(df)
    df = validate_countries(df)  # Check for unmapped countries (warns, doesn't fail)
    df = split_date(df)
    df = aggregate_business_keys(df)

    os.makedirs("data/processed", exist_ok=True)

    # --- Append or create ---
    if os.path.exists(OUTPUT_PATH):
        existing = pd.read_csv(OUTPUT_PATH, usecols=BASE_COLUMNS)
        incoming = df[BASE_COLUMNS].copy()
        combined = pd.concat([existing, incoming], ignore_index=True)
    else:
        combined = df[BASE_COLUMNS].copy()

    combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
    combined["count"] = pd.to_numeric(combined["count"], errors="coerce")
    combined["year"] = combined["date"].dt.year
    combined["month"] = combined["date"].dt.month

    df = aggregate_business_keys(combined)
    df = add_visa_metadata(df)

    df.to_csv(OUTPUT_PATH, index=False)

    # --- Update state ---
    processed.update(new_links)
    save_state(processed)

    print("Pipeline update complete.")
    print("Total rows:", len(df))
    print("Time:", round(time.time() - start, 2), "seconds")


if __name__ == "__main__":
    main()

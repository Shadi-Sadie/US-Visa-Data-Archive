"""Ingest manually downloaded .xlsx releases from data/raw/.

travel.state.gov sits behind a Cloudflare bot challenge that blocks automated
fetches, so new months have to be downloaded by hand in a browser and dropped
into data/raw/. This merges those files into the master dataset.
"""

import glob
import os
import sys

import pandas as pd

from src.extract import extract_date_from_filename, process_excel
from src.transform import (
    standardize_countries,
    validate_countries,
    split_date,
    aggregate_business_keys,
    add_visa_metadata,
)
from src.tracker import load_state, save_state


OUTPUT_PATH = "data/processed/visa_data.csv"
BASE_COLUMNS = ["date", "visa_program", "country", "visa_type", "count"]
RAW_DIR = "data/raw"


def classify_program(filename):
    # "NIV Issuances" must be tested first: it contains "IV Issuances".
    if "NIV Issuances" in filename:
        return "nonimmigrant"
    if "IV Issuances" in filename:
        return "immigrant"
    return None


def main():
    replace = "--replace" in sys.argv

    existing = pd.read_csv(OUTPUT_PATH, usecols=BASE_COLUMNS)
    existing["date"] = pd.to_datetime(existing["date"], errors="coerce")
    already = set(
        zip(existing["date"].dt.year, existing["date"].dt.month, existing["visa_program"])
    )

    pending = {"immigrant": [], "nonimmigrant": []}
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.xlsx"))):
        filename = os.path.basename(path)
        program = classify_program(filename)
        if program is None:
            print(f"Skipping (cannot classify program): {filename}")
            continue

        date = extract_date_from_filename(filename)
        if date is None:
            print(f"Skipping (cannot parse date): {filename}")
            continue

        stamp = pd.to_datetime(date, format="%B %Y")
        key = (stamp.year, stamp.month, program)
        if key in already and not replace:
            print(f"Skipping (already in dataset, pass --replace to override): {filename}")
            continue

        pending[program].append(path)

    if not any(pending.values()):
        print("No new files to ingest.")
        return

    frames = []
    for program, paths in pending.items():
        if paths:
            for p in paths:
                print(f"Ingesting {program}: {os.path.basename(p)}")
            frames.append(process_excel(paths, program))

    df = pd.concat(frames, ignore_index=True)

    df = standardize_countries(df)
    df = validate_countries(df)
    df = split_date(df)
    df = aggregate_business_keys(df)

    # Replace rather than append for any month being re-ingested, so re-running
    # never double-counts via the groupby-sum below.
    incoming_keys = set(zip(df["year"], df["month"], df["visa_program"]))
    existing_keys = list(
        zip(existing["date"].dt.year, existing["date"].dt.month, existing["visa_program"])
    )
    keep = [k not in incoming_keys for k in existing_keys]
    existing = existing[keep]

    combined = pd.concat([existing, df[BASE_COLUMNS]], ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
    combined["count"] = pd.to_numeric(combined["count"], errors="coerce")
    combined["year"] = combined["date"].dt.year
    combined["month"] = combined["date"].dt.month

    out = aggregate_business_keys(combined)
    out = add_visa_metadata(out)
    out.to_csv(OUTPUT_PATH, index=False)

    processed = load_state()
    processed.update(os.path.basename(p) for paths in pending.values() for p in paths)
    save_state(processed)

    print(f"\nWrote {OUTPUT_PATH}: {len(out)} rows")
    print("Now run: python build_visualization.py")


if __name__ == "__main__":
    main()

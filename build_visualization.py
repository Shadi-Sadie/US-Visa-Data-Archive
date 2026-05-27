import json
import os
import pandas as pd

INPUT_PATH = "data/processed/visa_data.csv"
OUTPUT_PATH = "docs/visa_aggregated.json"


def main():
    df = pd.read_csv(INPUT_PATH, usecols=["year", "visa_program", "program_type", "country", "count", "eligibility_pathway"])

    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)
    df["program_type"] = df["program_type"].astype(str).str.strip()
    df["eligibility_pathway"] = df["eligibility_pathway"].astype(str).str.strip()
    df["year"] = df["year"].astype(str)

    # --- totals_by_year ---
    by_year = df.groupby(["year", "visa_program"])["count"].sum().unstack(fill_value=0)
    by_year.columns = [c for c in by_year.columns]
    by_year["total"] = by_year.sum(axis=1)

    totals_by_year = {
        year: {
            "immigrant": int(row.get("immigrant", 0)),
            "nonimmigrant": int(row.get("nonimmigrant", 0)),
            "total": int(row["total"]),
        }
        for year, row in by_year.iterrows()
    }

    # --- country_data ---
    # Per-country-year totals per program
    totals = (
        df.groupby(["country", "year", "visa_program"])["count"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    totals["total"] = totals.get("immigrant", 0) + totals.get("nonimmigrant", 0)

    valid = df[df["program_type"] != "nan"]

    # Per-country-year-program breakdown by program_type
    breakdown = (
        valid.groupby(["country", "year", "visa_program", "program_type"])["count"]
        .sum()
    )

    # Per-country-year-program-program_type breakdown by eligibility_pathway
    visa_type_breakdown = (
        valid[valid["eligibility_pathway"] != "nan"]
        .groupby(["country", "year", "visa_program", "program_type", "eligibility_pathway"])["count"]
        .sum()
    )

    country_data = []
    for _, row in totals.iterrows():
        country = row["country"]
        year = row["year"]

        program_types = {"immigrant": {}, "nonimmigrant": {}}
        visa_types = {"immigrant": {}, "nonimmigrant": {}}

        for program in ("immigrant", "nonimmigrant"):
            try:
                pt = breakdown.loc[country, year, program]
                program_types[program] = {k: int(v) for k, v in pt.items()}
            except KeyError:
                pass

            for prog_type in program_types[program]:
                try:
                    vt = visa_type_breakdown.loc[country, year, program, prog_type]
                    visa_types[program][prog_type] = {k: int(v) for k, v in vt.items()}
                except KeyError:
                    pass

        country_data.append({
            "country": country,
            "year": year,
            "immigrant": int(row.get("immigrant", 0)),
            "nonimmigrant": int(row.get("nonimmigrant", 0)),
            "total": int(row["total"]),
            "program_types": program_types,
            "visa_types": visa_types,
        })

    os.makedirs("visualization", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump({"totals_by_year": totals_by_year, "country_data": country_data}, f, separators=(",", ":"))

    print(f"Wrote {len(country_data)} country-year entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

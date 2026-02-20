import os
import pdfplumber
import pandas as pd
import re
from urllib.parse import unquote
from src.scrape import download_pdf



COLUMN_MAPPING = {
    "country": [
        "place of birth",
        "foreign state of chargeability",
        "chargeability",
        "country of birth",
        "birth country",
        "nationality",
    ],
    "visa_type": [
        "visa class",
        "visa-class",
        "visaclass",
        "class",
        "visa",
    ],
    "count": [
        "issuances",
        "count",
        "number",
        "total",
        "quantity",
        "num",
    ],
}

REQUIRED_COLUMNS = {"country", "count", "visa_type"}


def normalize_columns(df):
    rename = {}
    for col in df.columns:
        col_l = str(col).lower().strip()
        for target, variants in COLUMN_MAPPING.items():
            if any(v in col_l for v in variants):
                rename[col] = target
                break
    return df.rename(columns=rename)


def extract_date_from_filename(filename):
    decoded = unquote(filename)

    # Match Month + Year (handles MAY2021, May-2021, May 2021, May%2021)
    m = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[A-Za-z]*[\s\-_]*?(20\d{2})",
        decoded,
        re.IGNORECASE,
    )

    if m:
        try:
            date_obj = pd.to_datetime(f"{m.group(1)} {m.group(2)}", errors="coerce")
            if pd.notna(date_obj):
                return date_obj.strftime("%B %Y")
        except:
            pass

    # Match Year + Month number (2021-03 or 2021_3)
    m = re.search(r"(20\d{2})[\s\-_]?(0?\d{1,2})", decoded)

    if m:
        try:
            date_obj = pd.to_datetime(f"{m.group(1)}-{m.group(2)}-01", errors="coerce")
            if pd.notna(date_obj):
                return date_obj.strftime("%B %Y")
        except:
            pass

    return None



def table_to_dataframe(table):
    if not table or len(table) < 2:
        return None

    def header_score(columns):
        target_score = 0
        column_hits = 0
        lowered = [str(c).lower().strip() if c else "" for c in columns]
        for col in lowered:
            if any(v in col for variants in COLUMN_MAPPING.values() for v in variants):
                column_hits += 1
        for target, variants in COLUMN_MAPPING.items():
            if any(any(v in col for v in variants) for col in lowered):
                target_score += 1
        return (column_hits, target_score)

    candidates = []
    # Common layouts:
    # 1) row 0 is header, data starts at row 1
    # 2) row 0 is title, row 1 is header, data starts at row 2
    if len(table) > 1:
        candidates.append((header_score(table[0]), pd.DataFrame(table[1:], columns=table[0])))
    if len(table) > 2:
        candidates.append((header_score(table[1]), pd.DataFrame(table[2:], columns=table[1])))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score, best_df = candidates[0]
    if best_score == (0, 0):
        # Fallback to first interpretation when no header keywords are detected.
        return pd.DataFrame(table[1:], columns=table[0])
    return best_df



def process_pdfs(pdf_urls, visa_program):

    all_rows = []

    for url in pdf_urls:

        pdf_path = download_pdf(url)
        filename = os.path.basename(pdf_path)
        date = extract_date_from_filename(filename)

        if date is None:
            raise ValueError(f"Could not parse month/year from filename: {filename}")

        pdf_rows = []
        skip_counts = {
            "empty_table": 0,
            "missing_required_columns": 0,
            "empty_after_cleaning": 0,
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    if not tables:
                        continue

                    for table_idx, table in enumerate(tables, 1):
                        df = table_to_dataframe(table)
                        if df is None:
                            skip_counts["empty_table"] += 1
                            continue

                        try:
                            df.columns = [str(c).strip() if c else "unnamed" for c in df.columns]
                            df = normalize_columns(df)

                            if not REQUIRED_COLUMNS.issubset(df.columns):
                                skip_counts["missing_required_columns"] += 1
                                continue

                            # Ensure country is string for filtering
                            df["country"] = df["country"].astype(str)

                            # Remove footnote/metadata rows and invalid entries
                            country_lower = df["country"].str.lower().str.strip()

                            df = df[
                                ~country_lower.str.contains("total", na=False)
                                & ~country_lower.str.contains("nationality", na=False)
                                & ~country_lower.str.contains("nationlity", na=False)  # Catch misspelled version
                                & ~country_lower.str.contains("unknown", na=False)
                                & ~country_lower.str.contains("other", na=False)
                                & ~country_lower.str.contains("non-nationality", na=False)
                                & ~country_lower.str.contains("non nationality", na=False)
                                & ~df["country"].str.startswith("*")  # Filter asterisk-prefixed rows
                            ]

                            df = df[df["visa_type"].notna()]
                            if df.empty:
                                skip_counts["empty_after_cleaning"] += 1
                                continue

                            df["date"] = date
                            df["visa_program"] = visa_program
                            pdf_rows.append(df)
                        except Exception as table_error:
                            raise RuntimeError(
                                f"Table parse failure in {filename} page {page_num} table {table_idx}: {table_error}"
                            ) from table_error
        except Exception as pdf_error:
            raise RuntimeError(f"Failed processing PDF {filename}: {pdf_error}") from pdf_error

        if not pdf_rows:
            raise RuntimeError(
                f"No valid rows extracted from {filename}. "
                f"Skips: {skip_counts}"
            )

        all_rows.extend(pdf_rows)

    if not all_rows:
        return pd.DataFrame()

    return pd.concat(all_rows, ignore_index=True)

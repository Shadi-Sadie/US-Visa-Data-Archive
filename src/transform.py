import os
import pandas as pd


# --- Country Standardization ---

tableau_countries = [
    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
    'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
    'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia',
    'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso',
    'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic',
    'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', "Cote d'Ivoire",
    'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Democratic Republic of the Congo', 'Denmark', 'Djibouti',
    'Dominica','Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea',
    'Estonia', 'Eswatini', 'Ethiopia', 'Falkland Islands', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia',
    'Georgia', 'Germany', 'Ghana', 'Greece', 'Greenland','Grenada', 'Guadeloupe', 'Guam','Guatemala', 'Guinea', 'Guinea-Bissau',
    'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq',
    'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya',
    'Kiribati',  'Kosovo','Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho',
    'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi',
    'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius',
    'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco',
    'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand',
    'Nicaragua', 'Niger', 'Nigeria', 'North Macedonia', 'North Korea','Norway', 'Oman', 'Pakistan', 'Palau',
    'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn Islands', 'Poland',
    'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia',
    'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe',
    'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia',
    'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 	'South Korea','South Sudan' , 	'Spain',
    'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan','Tajikistan',
    'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia',
    'Turkey', 'Turkmenistan', 'Turks and Caicos Islands','Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates',
    'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
    'Venezuela', 'Vietnam', 'Wallis and Futuna', 'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe'
]


COUNTRY_NAME_MAP = {
    "Korea, South": "South Korea",
    "Korea, North": "North Korea",
    "Antigua And Barbuda": "Antigua and Barbuda",
    "Great Britain and Northern Ireland": "United Kingdom",
    "Great Britain & Northern Ireland": "United Kingdom",
    "Bahamas, The": "Bahamas",
    "Burkina-Faso": "Burkina Faso",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Guinea - Bissau": "Guinea-Bissau",
    "Republic of the Congo": "Congo",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Kitts And Nevis": "Saint Kitts and Nevis",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Sudan, South": "South Sudan",
    "Turks And Caicos Islands": "Turks and Caicos Islands",
    "Gambia, The": "Gambia",
    "The Gambia": "Gambia",
    "eSwatini": "Eswatini",
    "**Eswatini": "Eswatini",
    "Eswatini*": "Eswatini",
    "Swaziland": "Eswatini",
    "Macedonia": "North Macedonia",
    "Micronesia, Federated States of": "Micronesia",
    "Czec Republic": "Czech Republic",
    # China variants (normalize all to 'China' or 'Taiwan')
    "China - mainland born": "China",
    "China - mainland": "China",
    "China - Mainland": "China",
    "China - Mainland born": "China",
    "China - Taiwan born": "Taiwan",
    "China - Taiwan": "Taiwan",
    "China-mainland": "China",
    "China-Mainland born": "China",
    "China-Taiwan": "Taiwan",
    "China-Taiwan born": "Taiwan",
    "China – mainland born": "China",  # en-dash variant
    "Congo, Republic of the": "Congo",
    "Congo, Democratic Republic of the": "Democratic Republic of the Congo",
    "Palestinian Authority Travel Document": "Palestine",
    "Hong Kong S.A.R.": "Hong Kong",
    "Kyrgystan": "Kyrgyzstan",
    "Macau S. A. R.": "China",
    'Macau S.A.R.': "China",
    "Macau": "China",
    "Federated States of Micronesia": "Micronesia",
    "Jerusalem": "Israel",

}


TERRITORY_MAP = {
  "Anguilla": "United Kingdom",
  "Aruba": "Netherlands",
  "Bermuda": "United Kingdom",
  "British Indian Ocean Territory": "United Kingdom",
  "British Virgin Islands": "United Kingdom",
  "British National Overseas (Hong Kong) Passport": "United Kingdom",
  "Burma": "Myanmar", # historical name correction
  "Cayman Islands": "United Kingdom",
  "Christmas Island": "Australia",
  "Cocos Islands": "Australia",
  "Cocos (Keeling) Islands": "Australia",
  "Cook Islands": "New Zealand",
  "Curacao": "Netherlands",
  "Faroe Islands": "Denmark",
  "Falkland Islands": "United Kingdom",
  "French Polynesia": "France",
  "Gibraltar": "United Kingdom",
  "Montserrat": "United Kingdom",
  "New Caledonia": "France",
  "Niue": "New Zealand",
  "Saint Martin": "France",
  "Sint Maarten": "Netherlands",
  'Saint Maarten': "Netherlands",
  "St. Helena": "United Kingdom",
  "St. Pierre and Miquelon": "France",
  "Cote D'Ivoire": "Cote d'Ivoire",  # Fix capitalization
  "Hong Kong S. A. R.": "Hong Kong",
  "Hong Kong S.A.R": "Hong Kong",
  "Hong Kong-BNO": "Hong Kong",
  "Marshall Islands, Republic of the": "Marshall Islands",
  "Northern Ireland (DV only)": "United Kingdom",
  "Pitcairn": "United Kingdom",
  "Republic of Palau": "Palau",
  "St Lucia": "Saint Lucia",
  "St. Vincent and The Grenadines": "Saint Vincent and the Grenadines",
  "Wallis and Futuna": "France",
  "Guadeloupe": "France"
}


def standardize_countries(df):
    # Clean up country names: strip spaces and lowercase
    df["country"] = df["country"].astype(str).str.strip()
    # Apply mapping (keys should also be lowercased for match)
    df["country"] = df["country"].replace(COUNTRY_NAME_MAP)
    df["country"] = df["country"].replace(TERRITORY_MAP)
    return df


def validate_countries(df):
    """Check for unmapped countries and print warnings; do not raise."""
    tableau_set = set(tableau_countries)
    unknown = set(df["country"]) - tableau_set

    if unknown:
        print(f"\nWARNING: Countries not in Tableau list: {sorted(unknown)}")
        print("These rows will still be included in the output.\n")

    return df


# --- Date Handling ---

def split_date(df):
    df["date"] = pd.to_datetime(df["date"], format="%B %Y", errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    
    # Clean count column: remove commas and convert to numeric
    if "count" in df.columns:
        df["count"] = df["count"].astype(str).str.replace(",", "")
        df["count"] = pd.to_numeric(df["count"], errors="coerce")
    
    return df


def aggregate_business_keys(df):
    """
    Collapse rows that map to the same analysis grain after country remapping.
    Grain: date + visa_program + country + visa_type.
    """
    key_cols = ["date", "year", "month", "visa_program", "country", "visa_type"]
    aggregated = (
        df.groupby(key_cols, dropna=False, as_index=False)
        .agg({"count": lambda s: s.sum(min_count=1)})
    )
    return aggregated



CODEBOOK_PATH = "data/reference/visa_codebook.csv"

def add_visa_metadata(df):

    codebook = pd.read_csv(CODEBOOK_PATH)

    # Ensure unique merge keys
    if codebook.duplicated(subset=["visa_type", "visa_program"]).any():
        raise ValueError("Duplicate visa_type + visa_program combinations in codebook")

    merged = df.merge(
        codebook,
        on=["visa_type", "visa_program"],   # clean and symmetric
        how="left"
    )

    missing = merged["program_type"].isna()

    if missing.any():
        unknown = merged.loc[missing].copy()
        os.makedirs("data/processed", exist_ok=True)
        out_path = "data/processed/unknown_visa_types.csv"
        unknown.to_csv(out_path, index=False)
        sample = unknown[["visa_type", "visa_program"]].drop_duplicates().head(20)
        print("\nWARNING: Unknown visa types detected (metadata columns will be null):")
        print(sample.to_string(index=False))
        print(f"Full rows dumped to: {out_path}\n")

    return merged

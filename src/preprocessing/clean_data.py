from pathlib import Path
import warnings

import pandas as pd
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

INPUT_FILE = Path("data/processed/jobs_merge.csv")
OUTPUT_FILE = Path("data/processed/jobs_clean.csv")

TRUE_VALUES = {"true", "1", "1.0", "yes"}
EMPTY_VALUES = ["", " ", "nan", "NaN", "None", "null"]

DATE_COLUMNS = ["first_activation", "activation", "expire"]

BOOL_COLUMNS = ["salary_visible", "internship", "remote", "urgent", "military"]

NUMERIC_COLUMNS = [
    "salary_min",
    "salary_max",
    "required_age_min",
    "required_age_max",
    "experience_years",
    "application_count",
]


def remove_html(text):
    if pd.isna(text):
        return text
    return BeautifulSoup(str(text), "html.parser").get_text(" ", strip=True)


def to_bool(series):
    # NOTE: astype(bool) on the string "False" gives True, so map explicitly.
    return series.astype("string").str.strip().str.lower().isin(TRUE_VALUES)


def main():

    print("Loading merged dataset...")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Initial rows: {len(df)}")

    df = df.drop_duplicates(subset="job_id").reset_index(drop=True)

    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "description" in df.columns:
        print("Removing HTML from descriptions (can take a few minutes)...")
        df["description"] = df["description"].apply(remove_html)

    for col in df.columns:
        s = df[col]
        if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
            s = s.astype("string").str.strip()
            df[col] = s.mask(s.isin(EMPTY_VALUES))

    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = to_bool(df[col])

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates().reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"Saved -> {OUTPUT_FILE}")
    print(f"Final rows: {len(df)}")


if __name__ == "__main__":
    main()

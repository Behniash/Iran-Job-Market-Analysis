from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup


INPUT_FILE = "data/processed/jobs_merge.csv"
OUTPUT_FILE = "data/processed/jobs_clean.csv"


def remove_html(text):
    if pd.isna(text):
        return text

    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def main():

    print("Loading merged dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Initial rows: {len(df)}")


    # Remove duplicate jobs
    df = df.drop_duplicates(subset="job_id").reset_index(drop=True)


    # Merge duplicated columns
    for col in ["internship", "remote", "urgent"]:
        if f"{col}_y" in df.columns:
            df[col] = df[f"{col}_y"].fillna(df.get(f"{col}_x"))

    drop_columns = [
        "internship_x",
        "internship_y",
        "remote_x",
        "remote_y",
        "urgent_x",
        "urgent_y",
    ]

    df.drop(columns=[c for c in drop_columns if c in df.columns], inplace=True,)


    # Convert dates
    date_columns = [
        "first_activation",
        "activation",
        "expire",
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")


    # Clean description HTML
    if "description" in df.columns:
        df["description"] = df["description"].apply(remove_html)

    # Strip only string columns
    object_cols = df.select_dtypes(include="object").columns

    for col in object_cols:
        df[col] = (df[col].astype("string").str.strip())


    # Normalize empty values
    df.replace({"": pd.NA, " ": pd.NA, "nan": pd.NA, "None": pd.NA,}, inplace=True,)


    # Boolean columns
    bool_columns = [
        "salary_visible",
        "internship",
        "remote",
        "urgent",
        "military",
    ]

    for col in bool_columns:
        if col in df.columns:
            df[col] = (df[col].fillna(False).astype(bool))


    # Numeric columns
    numeric_columns = [
        "salary_min",
        "salary_max",
        "required_age_min",
        "required_age_max",
        "experience_years",
        "application_count",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


    # Remove exact duplicates
    df.drop_duplicates(inplace=True)

    # Save
    output_dir = Path("data/processed")

    output_dir.mkdir(parents=True, exist_ok=True)


    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig",)

    print(f"Saved -> {OUTPUT_FILE}")

    print(f"Final rows: {len(df)}")

if __name__ == "__main__":
    main()
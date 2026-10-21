from pathlib import Path

import pandas as pd

JOB_LIST_FILE = Path("data/raw/jobvision/job_list.csv")
JOB_DETAILS_FILE = Path("data/raw/jobvision/job_details.csv")
OUTPUT_FILE = Path("data/processed/jobs_merge.csv")


def prepare_ids(df):
    df["job_id"] = pd.to_numeric(df["job_id"], errors="coerce")
    df = df.dropna(subset=["job_id"]).copy()
    df["job_id"] = df["job_id"].astype("int64")
    return df


def main():

    job_list = prepare_ids(pd.read_csv(JOB_LIST_FILE, low_memory=False))
    job_details = prepare_ids(pd.read_csv(JOB_DETAILS_FILE, low_memory=False))

    print("Job List:", job_list.shape)
    print("Job Details:", job_details.shape)

    # Same job can appear with different keywords -> keep one row,
    # but combine all its keywords into one column.
    before = len(job_list)

    keywords = (
        job_list.groupby("job_id")["keyword"]
        .agg(lambda s: "|".join(sorted(set(s.dropna().astype(str)))))
        .reset_index()
    )

    job_list = (
        job_list.drop_duplicates(subset="job_id", keep="first")
        .drop(columns="keyword")
        .merge(keywords, on="job_id", how="left")
        .reset_index(drop=True)
    )

    print(f"Removed duplicated job_list rows: {before - len(job_list)}")

    # Remove duplicated details
    before = len(job_details)

    job_details = job_details.drop_duplicates(subset="job_id", keep="last").reset_index(drop=True)

    print(f"Removed duplicated job_details rows: {before - len(job_details)}")

    # source / scraped_at: keep the job_list version
    job_details = job_details.drop(
        columns=[c for c in ["source", "scraped_at"] if c in job_details.columns]
    )

    # Columns that exist in both files (e.g. internship, remote, urgent):
    # details version wins, job_list version is the fallback.
    overlap = [c for c in job_details.columns if c in job_list.columns and c != "job_id"]
    print("Overlapping columns:", overlap)

    df = job_list.merge(
        job_details,
        on="job_id",
        how="left",
        suffixes=("_list", ""),
        validate="one_to_one",
    )

    for col in overlap:
        df[col] = df[col].combine_first(df[f"{col}_list"])
        df.drop(columns=f"{col}_list", inplace=True)

    print("Merged:", df.shape)

    if "description" in df.columns:
        missing = df["description"].isna().sum()
        print(f"Missing Details: {missing} ({missing / len(df):.2%})")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\nSaved Successfully")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()

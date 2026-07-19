from pathlib import Path
import pandas as pd


JOB_LIST_FILE = Path("data/raw/jobvision/job_list.csv")

JOB_DETAILS_FILE = Path("data/raw/jobvision/job_details.csv")

OUTPUT_FILE = Path("data/processed/jobs_merge.csv")


def main():

    # Load raw data
    job_list = pd.read_csv(JOB_LIST_FILE)

    job_details = pd.read_csv(JOB_DETAILS_FILE)


    print("Job List:", job_list.shape)
    print("Job Details:", job_details.shape)


    # Remove duplicated jobs from job_list
    # Same job can appear with different keywords

    before = len(job_list)

    job_list = (job_list.drop_duplicates(subset=["job_id"], keep="first").reset_index(drop=True))

    print(f"Removed duplicated job_list rows: {before - len(job_list)}")


    # Remove duplicated details
    before = len(job_details)

    job_details = (job_details.drop_duplicates(subset=["job_id"], keep="last").reset_index(drop=True))

    print(f"Removed duplicated job_details rows: {before - len(job_details)}")


    # Remove overlapping columns
    # Keep details version
    columns_to_remove = [
        "internship",
        "remote",
        "urgent",
        "source",
        "scraped_at"
    ]


    job_details = job_details.drop(columns=[col for col in columns_to_remove if col in job_details.columns])

    print("Job Details after cleaning:", job_details.shape)


    # Merge
    df = job_list.merge(job_details, on="job_id", how="left", validate="one_to_one")
    print("Merged:", df.shape)

    # Check missing details
    if "description" in df.columns:

        missing = (df["description"].isna().sum())

        print(f"Missing Details: {missing} " f"({missing / len(df):.2%})")


    # Save processed dataset
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\nSaved Successfully")

    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
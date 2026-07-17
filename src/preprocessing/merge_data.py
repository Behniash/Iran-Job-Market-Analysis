from pathlib import Path
import pandas as pd

job_list = pd.read_csv("data/raw/job_list.csv")
job_details = pd.read_csv("data/raw/job_details.csv")

df = job_list.merge(job_details, on="job_id", how="left")

Path("data/processed").mkdir(parents=True, exist_ok=True)

df.to_csv("data/processed/jobs_merge.csv", index=False, encoding="utf-8-sig")

print(df.shape)

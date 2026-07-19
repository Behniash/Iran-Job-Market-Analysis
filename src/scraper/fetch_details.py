from pathlib import Path
import random
import time
import pandas as pd
import requests
from datetime import datetime
from src.api.api_client import JobVisionAPI

INPUT_FILE = Path("data/raw/jobvision/job_list.csv")
OUTPUT_FILE = Path("data/raw/jobvision/job_details.csv")

CHECKPOINT_EVERY = 200
MAX_RETRIES = 3

api = JobVisionAPI()


def fetch_detail(job_id):
    for attempt in range(MAX_RETRIES):
        try:
            return api.get_job_detail(job_id)["data"]
        except requests.exceptions.RequestException as e:
            print(f"[Retry {attempt+1}/{MAX_RETRIES}] Job {job_id}: {e}")
            time.sleep(2 ** attempt)
    return None


def load_existing():
    if OUTPUT_FILE.exists():
        df = pd.read_csv(OUTPUT_FILE)
        return df.to_dict("records"), set(df["job_id"])
    return [], set()


def save(records):
    df = pd.DataFrame(records)
    df.drop_duplicates(subset="job_id", inplace=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")


def main():
    jobs = pd.read_csv(INPUT_FILE)
    details, scraped = load_existing()

    print(f"Jobs in input: {len(jobs)}")
    print(f"Already scraped: {len(scraped)}")

    new_count = 0

    for i, row in enumerate(jobs.itertuples(index=False), start=1):
        job_id = row.job_id

        if job_id in scraped:
            continue

        print(f"{i}/{len(jobs)} -> {job_id}")

        data = fetch_detail(job_id)
        if data is None:
            continue

        company = data.get("company") or {}
        salary = data.get("salary") or {}

        details.append({
            "source": "jobvision",
            "scraped_at": datetime.now().strftime("%Y-%m-%d"),
            "job_id": job_id,
            "description": data.get("description"),
            "work_type": (data.get("workType") or {}).get("titleEn"),
            "seniority": (data.get("seniorityLevel") or {}).get("titleEn"),
            "category": ",".join(x.get("titleEn","") for x in (data.get("jobCategories") or [])),
            "company_size": (company.get("size") or {}).get("titleEn"),
            "industries": ",".join(x.get("titleEn","") for x in (company.get("industries") or [])),
            "benefits": ",".join(x.get("titleEn","") for x in (data.get("benefits") or [])),
            "salary_title": salary.get("titleEn"),
            "salary_min": salary.get("min"),
            "salary_max": salary.get("max"),
            "gender": (data.get("gender") or {}).get("titleEn"),
            "required_age_min": data.get("requiredAgeMin"),
            "required_age_max": data.get("requiredAgeMax"),
            "military": data.get("shouldDoneMilitaryService"),
            "internship": data.get("isInternship"),
            "remote": data.get("isRemote"),
            "urgent": data.get("isUrgent"),
            "work_days": data.get("workDays"),
            "business_trip": data.get("businessTrip"),
            "software": ",".join(x.get("software",{}).get("titleEn","") for x in (data.get("softwareRequirements") or [])),
            "software_levels": ",".join(x.get("skill",{}).get("titleEn","") for x in (data.get("softwareRequirements") or [])),
            "first_activation": (data.get("firstActivationTime") or {}).get("date"),
            "activation": (data.get("activationTime") or {}).get("date"),
            "expire": (data.get("expireTime") or {}).get("date"),
            "application_count": data.get("insightApplicationCount"),
        })

        scraped.add(job_id)
        new_count += 1

        if new_count % CHECKPOINT_EVERY == 0:
            save(details)
            print(f"[Checkpoint] saved {len(details)} rows")

        time.sleep(random.uniform(0.1,0.2))

    save(details)
    print("Done.")

if __name__ == "__main__":
    main()

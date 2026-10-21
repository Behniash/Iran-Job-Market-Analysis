from datetime import datetime
from pathlib import Path
import random
import time

import pandas as pd
import requests

from src.api.api_client import JobVisionAPI

INPUT_FILE = Path("data/raw/jobvision/job_list.csv")
OUTPUT_FILE = Path("data/raw/jobvision/job_details.csv")
FAILED_FILE = Path("data/raw/jobvision/failed_ids.txt")

CHECKPOINT_EVERY = 200
MAX_RETRIES = 3

api = JobVisionAPI()



def get_in(d, *keys, default=None):
    """Safe nested get: get_in(data, "a", "b") -> data["a"]["b"] or default."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return default if d is None else d


def join_titles(items, *path):
    """Join values found at `path` inside each item of a list (None-safe)."""
    if not isinstance(items, list):
        return ""
    values = []
    for x in items:
        v = x if isinstance(x, str) else get_in(x, *path)
        if v:
            values.append(str(v))
    return ",".join(values)



def fetch_detail(job_id):
    """Returns (data, permanent_failure)."""
    for attempt in range(MAX_RETRIES):
        try:
            payload = api.get_job_detail(job_id)
            data = payload.get("data") if isinstance(payload, dict) else None
            if data is None:
                return None, True
            return data, False

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else None

            if code == 429:
                print(f"[429] Rate limited, sleeping 30s (Job {job_id})")
                time.sleep(30)
                continue

            if code is not None and 400 <= code < 500:
                print(f"[HTTP {code}] Job {job_id} skipped")
                return None, True

            print(f"[Retry {attempt + 1}/{MAX_RETRIES}] Job {job_id}: {e}")

        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"[Retry {attempt + 1}/{MAX_RETRIES}] Job {job_id}: {e}")

        time.sleep(2 ** attempt)

    return None, False



def build_record(job_id, data):
    company = data.get("company") or {}
    salary = data.get("salary") or {}
    software = data.get("softwareRequirements")

    return {
        "source": "jobvision",
        "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        "job_id": job_id,
        "description": data.get("description"),
        "work_type": get_in(data, "workType", "titleEn"),
        "seniority": get_in(data, "seniorityLevel", "titleEn"),
        "category": join_titles(data.get("jobCategories"), "titleEn"),
        "company_size": get_in(company, "size", "titleEn"),
        "industries": join_titles(company.get("industries"), "titleEn"),
        "benefits": join_titles(data.get("benefits"), "titleEn"),
        "salary_title": salary.get("titleEn"),
        "salary_min": salary.get("min"),
        "salary_max": salary.get("max"),
        "gender": get_in(data, "gender", "titleEn"),
        "required_age_min": data.get("requiredAgeMin"),
        "required_age_max": data.get("requiredAgeMax"),
        "military": data.get("shouldDoneMilitaryService"),
        "internship": data.get("isInternship"),
        "remote": data.get("isRemote"),
        "urgent": data.get("isUrgent"),
        "work_days": data.get("workDays"),
        "business_trip": data.get("businessTrip"),
        "software": join_titles(software, "software", "titleEn"),
        "software_levels": join_titles(software, "skill", "titleEn"),
        "first_activation": get_in(data, "firstActivationTime", "date"),
        "activation": get_in(data, "activationTime", "date"),
        "expire": get_in(data, "expireTime", "date"),
        "application_count": data.get("insightApplicationCount"),
    }



def load_existing():
    if OUTPUT_FILE.exists():
        df = pd.read_csv(OUTPUT_FILE, low_memory=False)
        df = df.dropna(subset=["job_id"])
        df["job_id"] = df["job_id"].astype("int64")
        return df.to_dict("records"), set(df["job_id"])
    return [], set()


def load_failed():
    if FAILED_FILE.exists():
        return {int(x) for x in FAILED_FILE.read_text().split() if x.strip().isdigit()}
    return set()


def mark_failed(job_id, failed):
    failed.add(job_id)
    FAILED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FAILED_FILE, "a") as f:
        f.write(f"{job_id}\n")


def save(records):
    df = pd.DataFrame(records)
    df.drop_duplicates(subset="job_id", keep="last", inplace=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    tmp = OUTPUT_FILE.with_suffix(".csv.tmp")
    df.to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(OUTPUT_FILE)



def main():
    jobs = pd.read_csv(INPUT_FILE, usecols=["job_id"], low_memory=False)
    all_ids = jobs["job_id"].dropna().astype("int64").drop_duplicates().tolist()

    details, scraped = load_existing()
    failed = load_failed()

    todo = [j for j in all_ids if j not in scraped and j not in failed]

    print(f"Rows in job_list      : {len(jobs)}")
    print(f"Unique job ids        : {len(all_ids)}")
    print(f"Already scraped       : {len(scraped)}")
    print(f"Known failed (skipped): {len(failed)}")
    print(f"To scrape now         : {len(todo)}")

    new_count = 0

    try:
        for i, job_id in enumerate(todo, start=1):
            print(f"{i}/{len(todo)} -> {job_id}")

            data, permanent = fetch_detail(job_id)

            if data is None:
                if permanent:
                    mark_failed(job_id, failed)
                continue

            try:
                record = build_record(job_id, data)
            except Exception as e:
                print(f"[Parse error] Job {job_id}: {e}")
                continue

            details.append(record)
            scraped.add(job_id)
            new_count += 1

            if new_count % CHECKPOINT_EVERY == 0:
                save(details)
                print(f"[Checkpoint] saved {len(details)} rows")

            time.sleep(random.uniform(0.1, 0.2))

    except KeyboardInterrupt:
        print("\nInterrupted by user, saving progress...")
        save(details)
        print(f"Saved {len(details)} rows. Run again to resume.")
        raise

    finally:
        if details:
            save(details)

    print("Done.")



if __name__ == "__main__":
    main()

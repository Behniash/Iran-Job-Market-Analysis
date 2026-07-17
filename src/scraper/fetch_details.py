from pathlib import Path
import pandas as pd
from src.api.api_client import JobVisionAPI

api = JobVisionAPI()

jobs = pd.read_csv("data/raw/job_list.csv")

details = []

for i, row in jobs.iterrows():

    job_id = row["job_id"]

    print(f"{i+1}/{len(jobs)} -> {job_id}")

    try:

        response = api.get_job_detail(job_id)
        data = response["data"]

        details.append({
            "job_id": job_id,

            "description": data.get("description"),

            "work_type": (data.get("workType") or {}).get("titleEn"),

            "seniority": (data.get("seniorityLevel") or {}).get("titleEn"),

            "category": ",".join(x.get("titleEn", "") for x in (data.get("jobCategories") or [])),

            "company_size": ((data.get("company") or {}).get("size") or {}).get("titleEn"),

            "industries": ",".join(x.get("titleEn", "") for x in ((data.get("company") or {}).get("industries") or [])),

            "benefits": ",".join(x.get("titleEn", "") for x in (data.get("benefits") or [])),

            "salary_title":(data.get("salary") or {}).get("titleEn"),

            "salary_min":(data.get("salary") or {}).get("min"),

            "salary_max":(data.get("salary") or {}).get("max"),

            "gender":(data.get("gender") or {}).get("titleEn"),

            "required_age_min":data.get("requiredAgeMin"),

            "required_age_max":data.get("requiredAgeMax"),

            "military":data.get("shouldDoneMilitaryService"),

            "internship":data.get("isInternship"),

            "remote":data.get("isRemote"),

            "urgent":data.get("isUrgent"),

            "work_days":data.get("workDays"),

            "business_trip":data.get("businessTrip"),

            "software": ",".join(x.get("software", {}).get("titleEn", "") for x in (data.get("softwareRequirements") or [])),

            "software_levels": ",".join(x.get("skill", {}).get("titleEn", "") for x in (data.get("softwareRequirements") or [])),

            "first_activation": (data.get("firstActivationTime") or {}).get("date"),

            "activation": (data.get("activationTime") or {}).get("date"),

            "expire": (data.get("expireTime") or {}).get("date"),

            "application_count": data.get("insightApplicationCount")

        })

    except Exception as e:

        print(job_id, e)

detail_df = pd.DataFrame(details)

Path("data/raw").mkdir(parents=True, exist_ok=True)

detail_df.to_csv("data/raw/job_details.csv", index=False, encoding="utf-8-sig")
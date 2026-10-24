from datetime import datetime
from pathlib import Path
import random
import time

import pandas as pd
import requests

from src.api.api_client import JobVisionAPI

PAGE_SIZE = 30
MAX_PAGES = 200
MAX_CONSECUTIVE_FAILS = 3
STOP_AFTER_STALE_PAGES = 2   

OUTPUT_DIR = Path("data/raw/jobvision")
OUTPUT_FILE = OUTPUT_DIR / "job_list.csv"

KEYWORDS = [
    # Backend
    "python", "django", "fastapi", "flask", "backend", "backend developer",
    "software engineer", "software developer", "developer", "programmer",
    "java", "spring", "spring boot", "php", "laravel", ".net", "asp.net",
    "nodejs", "express",

    # Frontend
    "frontend", "frontend developer", "react", "reactjs", "vue", "vuejs",
    "angular", "javascript", "typescript", "nextjs", "html", "css",

    # Mobile
    "android", "ios", "flutter", "react native", "kotlin", "swift",

    # DevOps & Cloud
    "devops", "linux", "docker", "kubernetes", "aws", "azure", "gcp",
    "terraform", "jenkins",

    # Database
    "sql", "mysql", "postgresql", "oracle", "mongodb", "redis",
    "database administrator",

    # Data & AI
    "data analyst", "data engineer", "data scientist", "business intelligence",
    "power bi", "tableau", "etl", "machine learning", "deep learning",
    "artificial intelligence", "computer vision", "nlp", "spark", "airflow",
    "hadoop",

    # QA
    "qa", "quality assurance", "test engineer", "automation tester",

    # Security
    "security", "cyber security", "penetration tester", "soc",

    # Infrastructure
    "network", "network engineer", "system administrator", "cloud engineer",

    # Persian
    "برنامه نویس", "توسعه دهنده", "برنامه نویس پایتون", "برنامه نویس جاوا",
    "برنامه نویس وب", "برنامه نویس بک اند", "برنامه نویس فرانت اند",
    "برنامه نویس اندروید", "برنامه نویس فلاتر", "مهندس نرم افزار",
    "تحلیلگر داده", "مهندس داده", "دانشمند داده", "هوش مصنوعی",
    "یادگیری ماشین", "دواپس", "کارشناس شبکه", "ادمین شبکه",
]


class JobFetcher:

    def __init__(self):
        self.api = JobVisionAPI()

    def fetch_page(self, keyword, page):
        retries = 5

        for attempt in range(retries):
            try:
                response = self.api.get_job_list(keyword=keyword, page=page)
                data = response.get("data")
                if data is not None:
                    return data
                print(f"Empty data -> {keyword} | Page {page}")

            except requests.exceptions.ReadTimeout:
                print(f"Timeout -> {keyword} | Page {page} ({attempt + 1}/{retries})")

            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"Request Error -> {keyword} | Page {page}")
                print(e)

            time.sleep(2 ** attempt)

        print(f"Skipped Page {page}")
        return None

    def parse_jobs(self, data, keyword):
        jobs = []

        for job in data.get("jobPosts") or []:
            try:
                location = job.get("location") or {}
                province = location.get("province") or {}
                city = location.get("city") or {}

                company = job.get("company") or {}
                properties = job.get("properties") or {}

                jobs.append({
                    "source": "jobvision",
                    "scraped_at": datetime.now().strftime("%Y-%m-%d"),
                    "keyword": keyword,
                    "job_id": job.get("id"),
                    "title": job.get("title"),
                    "company": company.get("nameFa"),
                    "province": province.get("titleFa"),
                    "city": city.get("titleFa"),
                    "salary_visible": properties.get("salaryCanBeShown"),
                    "experience_years": properties.get("requiredRelatedExperienceYears"),
                })

            except Exception as e:
                print(f"Skipped Job {job.get('id')} -> {e}")

        return jobs

    def fetch_keyword(self, keyword, known_ids=frozenset(), update=False):

        page = 1
        fails = 0
        stale_pages = 0
        all_jobs = []
        seen_ids = set()

        while page <= MAX_PAGES:
            print(f"\nKeyword = {keyword} | Page = {page}")

            data = self.fetch_page(keyword, page)

            if data is None:
                fails += 1
                if fails >= MAX_CONSECUTIVE_FAILS:
                    print(f"Too many failed pages, stopping keyword: {keyword}")
                    break
                page += 1
                continue

            fails = 0

            jobs = self.parse_jobs(data, keyword)
            if not jobs:
                break

            unseen = [j for j in jobs if j["job_id"] not in seen_ids]
            if not unseen:
                print("Repeated page -> stopping keyword")
                break
            seen_ids.update(j["job_id"] for j in unseen)

            fresh = [j for j in unseen if j["job_id"] not in known_ids]
            all_jobs.extend(fresh)

            print(f"Page jobs: {len(jobs)} | New: {len(fresh)} | Total new: {len(all_jobs)}")

            if update:
                if fresh:
                    stale_pages = 0
                else:
                    stale_pages += 1
                    if stale_pages >= STOP_AFTER_STALE_PAGES:
                        print("No new jobs in recent pages -> stopping keyword")
                        break

            if len(jobs) < (data.get("pageSize") or PAGE_SIZE):
                break

            page += 1
            time.sleep(random.uniform(0.8, 1.5))

        return all_jobs


def save(df):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT_FILE.with_suffix(".csv.tmp")
    df.to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(OUTPUT_FILE)


def main(update=False):
    fetcher = JobFetcher()

    if OUTPUT_FILE.exists():
        all_df = pd.read_csv(OUTPUT_FILE, low_memory=False)
        all_df = all_df.dropna(subset=["job_id"])
        all_df["job_id"] = all_df["job_id"].astype("int64")
        done_keywords = set(all_df["keyword"].dropna().astype(str))
        known = all_df.groupby("keyword")["job_id"].agg(set).to_dict()
    else:
        all_df = pd.DataFrame()
        done_keywords = set()
        known = {}

    ids_before = set(all_df["job_id"]) if not all_df.empty else set()

    print(f"Mode: {'UPDATE' if update else 'FIRST RUN'}")
    print(f"Already completed keywords: {len(done_keywords)}")

    for keyword in KEYWORDS:

        already_done = keyword in done_keywords

        if already_done and not update:
            print(f"Skip (already done): {keyword}")
            continue

        print("-" * 60)
        print(f"Start Keyword : {keyword}")
        print("-" * 60)

        try:
            jobs = fetcher.fetch_keyword(
                keyword,
                known_ids=known.get(keyword, set()),
                update=update and already_done,
            )
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break

        if jobs:
            df = pd.DataFrame(jobs)
            all_df = df if all_df.empty else pd.concat([all_df, df], ignore_index=True)
            all_df.drop_duplicates(subset=["source", "job_id", "keyword"], inplace=True)
            save(all_df)
            known.setdefault(keyword, set()).update(df["job_id"])
            print(f"Saved -> {len(all_df)} rows")

        time.sleep(random.uniform(2, 4))

    print("\nFinished.")
    if not all_df.empty:
        new_ids = set(all_df["job_id"]) - ids_before
        print(f"Total rows      : {len(all_df)}")
        print(f"Unique jobs     : {all_df['job_id'].nunique()}")
        print(f"New unique jobs : {len(new_ids)}")


if __name__ == "__main__":
    main()

from pathlib import Path
import random
import time
import pandas as pd
import requests
from src.api.api_client import JobVisionAPI
from datetime import datetime

KEYWORDS = [

    # Backend
    "python",
    "django",
    "fastapi",
    "flask",
    "backend",
    "backend developer",
    "software engineer",
    "software developer",
    "developer",
    "programmer",
    "java",
    "spring",
    "spring boot",
    "php",
    "laravel",
    ".net",
    "asp.net",
    "nodejs",
    "express",

    # Frontend
    "frontend",
    "frontend developer",
    "react",
    "reactjs",
    "vue",
    "vuejs",
    "angular",
    "javascript",
    "typescript",
    "nextjs",
    "html",
    "css",

    # Mobile
    "android",
    "ios",
    "flutter",
    "react native",
    "kotlin",
    "swift",

    # DevOps & Cloud
    "devops",
    "linux",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "terraform",
    "jenkins",

    # Database
    "sql",
    "mysql",
    "postgresql",
    "oracle",
    "mongodb",
    "redis",
    "database administrator",

    # Data & AI
    "data analyst",
    "data engineer",
    "data scientist",
    "business intelligence",
    "power bi",
    "tableau",
    "etl",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "computer vision",
    "nlp",
    "spark",
    "airflow",
    "hadoop",

    # QA
    "qa",
    "quality assurance",
    "test engineer",
    "automation tester",

    # Security
    "security",
    "cyber security",
    "penetration tester",
    "soc",

    # Infrastructure
    "network",
    "network engineer",
    "system administrator",
    "cloud engineer",

    # Persian
    "برنامه نویس",
    "توسعه دهنده",
    "برنامه نویس پایتون",
    "برنامه نویس جاوا",
    "برنامه نویس وب",
    "برنامه نویس بک اند",
    "برنامه نویس فرانت اند",
    "برنامه نویس اندروید",
    "برنامه نویس فلاتر",
    "مهندس نرم افزار",
    "تحلیلگر داده",
    "مهندس داده",
    "دانشمند داده",
    "هوش مصنوعی",
    "یادگیری ماشین",
    "دواپس",
    "کارشناس شبکه",
    "ادمین شبکه",
]


class JobFetcher:

    def __init__(self):
        self.api = JobVisionAPI()

    def fetch_page(self, keyword, page):

        retries = 5

        for attempt in range(retries):

            try:
                response = self.api.get_job_list(keyword=keyword, page=page)
                return response["data"]
            except requests.exceptions.ReadTimeout:

                print(f"Timeout -> {keyword} | Page {page} " f"({attempt + 1}/{retries})")

            except requests.exceptions.RequestException as e:

                print(
                    f"Request Error -> {keyword} | Page {page}"
                )
                print(e)

            time.sleep(2 ** attempt)

        print(f"Skipped Page {page}")

        return None

    def parse_jobs(self, data, keyword):

        jobs = []

        for job in data.get("jobPosts", []):

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

    def fetch_keyword(self, keyword):

        page = 1

        all_jobs = []

        while True:

            print(f"\nKeyword = {keyword} | Page = {page}")

            data = self.fetch_page(keyword, page)

            if data is None:
                page += 1
                continue

            jobs = self.parse_jobs(data, keyword)

            if not jobs:
                break

            all_jobs.extend(jobs)

            print(f"Collected: {len(jobs)} jobs")

            if len(jobs) < data["pageSize"]:
                break

            page += 1

            time.sleep(random.uniform(0.8, 1.5))

        return all_jobs


if __name__ == "__main__":

    fetcher = JobFetcher()

    output_dir = Path("data/raw/jobvision")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "job_list.csv"

    if output_file.exists():

        all_df = pd.read_csv(output_file)

    else:

        all_df = pd.DataFrame()

    for keyword in KEYWORDS:

        print("-" * 60)
        print(f"Start Keyword : {keyword}")
        print("-" * 60)

        jobs = fetcher.fetch_keyword(keyword)

        if jobs:

            df = pd.DataFrame(jobs)

            all_df = pd.concat([all_df, df], ignore_index=True)

            all_df.drop_duplicates(subset=["source", "job_id", "keyword"], inplace=True)

            all_df.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"Saved -> {len(all_df)} unique jobs")

        time.sleep(random.uniform(2, 4))

    print("\nFinished.")
    print(f"Total Unique Jobs : {len(all_df)}")
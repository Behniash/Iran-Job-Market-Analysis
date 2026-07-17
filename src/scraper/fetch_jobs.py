from pathlib import Path
import pandas as pd
from src.api.api_client import JobVisionAPI


KEYWORDS = [
    # Backend
    "python",
    "django",
    "fastapi",
    "flask",
    "backend",
    "backend developer",
    "software engineer",
    "developer",
    "programmer",

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

    # Mobile
    "android",
    "ios",
    "flutter",
    "react native",
    "kotlin",
    "swift",

    # DevOps
    "devops",
    "linux",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "terraform",
    "ansible",
    "jenkins",

    # Database
    "sql",
    "mysql",
    "postgresql",
    "oracle",
    "mongodb",
    "redis",

    # Data
    "data scientist",
    "data analyst",
    "data engineer",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "computer vision",
    "nlp",
    "power bi",
    "tableau",
    "etl",
    "spark",
    "airflow",
    "hadoop",

    # QA
    "qa",
    "test engineer",
    "automation",

    # Security
    "security",
    "cyber security",
    "penetration tester",

    # General IT
    "it",
    "network",
    "system administrator",
    "database administrator",
    "cloud engineer"
]


class JobFetcher:

    def __init__(self):
        self.api = JobVisionAPI()

    def fetch_page(self, keyword, page):
        response = self.api.get_job_list(keyword=keyword, page=page)
        return response["data"]

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

                    "keyword": keyword,

                    "job_id": job.get("id"),

                    "title": job.get("title"),

                    "company": company.get("nameFa"),

                    "province": province.get("titleFa"),

                    "city": city.get("titleFa"),

                    "salary_visible": properties.get("salaryCanBeShown"),

                    "internship": properties.get("isInternship"),

                    "remote": properties.get("isRemote"),

                    "urgent": properties.get("isUrgent"),

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

            jobs = self.parse_jobs(data, keyword)

            if not jobs:
                break

            all_jobs.extend(jobs)

            print(f"Collected: {len(jobs)} jobs")

            if len(jobs) < data["pageSize"]:
                break
            
            page += 1

        return all_jobs


if __name__ == "__main__":

    fetcher = JobFetcher()

    rows = []

    for keyword in KEYWORDS:

        rows.extend(
            fetcher.fetch_keyword(keyword)
        )

    df = pd.DataFrame(rows)

    print(f"\nBefore Remove Duplicates : {len(df)}")

    df.drop_duplicates(
        subset="job_id",
        inplace=True
    )

    print(f"After Remove Duplicates  : {len(df)}")

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_dir / "job_list.csv", index=False, encoding="utf-8-sig")

    print("\nSaved Successfully.")
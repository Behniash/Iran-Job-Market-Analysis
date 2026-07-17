import requests
from .endpoints import (JOB_LIST_ENDPOINT, JOB_DETAIL_ENDPOINT)


class JobVisionAPI:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://jobvision.ir",
            "Referer": "https://jobvision.ir/",
            "User-Agent":"Mozilla/5.0"
        })


    def get_job_list(self, keyword, page=1, page_size=30, sort_by=1):
        payload = {
            "pageSize": page_size,
            "requestedPage": page,
            "sortBy": sort_by,
            "keyword": keyword,
            "searchId": None
        }

        response = self.session.post(JOB_LIST_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()


    def get_job_detail(self, job_id):
        response = self.session.get(JOB_DETAIL_ENDPOINT, params={"jobPostId": job_id}, timeout=30)
        response.raise_for_status()
        return response.json()
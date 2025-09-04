import requests
from bs4 import BeautifulSoup

class JobScraper:
    def scrape_remoteok(self):
        url = "https://remoteok.com/"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = []
        for job in soup.select("tr.job"):
            title = job.select_one("h2").text.strip() if job.select_one("h2") else None
            company = job.select_one(".companyLink").text.strip() if job.select_one(".companyLink") else None
            link = "https://remoteok.com" + job.get("data-href", "")
            jobs.append({"title": title, "company": company, "link": link})
        return jobs

    def scrape_example_site(self):
        # 👉 Later add new scrapers here
        return []

import requests
from bs4 import BeautifulSoup
from datetime import datetime

class JobScraper:
    def __init__(self):
        # ✅ Sources list, unaweza kuongeza baadaye
        self.sources = [
            {"name": "RemoteOK", "url": "https://remoteok.com/api", "type": "api", "deadline_field": None},
            {"name": "JobwebTanzania", "url": "https://www.jobwebtanzania.com/", "type": "html", "selector": ".job-listing a", "deadline_field": None},
            {"name": "GreatTanzaniaJobs", "url": "https://www.greattanzaniajobs.com/jobs/", "type": "html", "selector": ".job-list a", "deadline_field": None},
            {"name": "BrighterMondayTZ", "url": "https://www.brightermonday.co.tz/api/jobs", "type": "api", "deadline_field": "expires_at"},
            {"name": "LinkedInRemoteTZ", "url": "https://www.linkedin.com/jobs-guest/jobs/api/remote-tanzania", "type": "api", "deadline_field": "expirationTimestamp"},
            {"name": "GlassdoorTZ", "url": "https://www.glassdoor.com/Job/tanzania-remote-jobs-SRCH_IL.0,7_IS287_KO8,14.htm", "type": "html", "selector": ".jobCard a", "deadline_field": None},
            {"name": "Indeed", "url": "https://www.indeed.com/jobs?q=remote&l=Tanzania", "type": "html", "selector": ".jobTitle a", "deadline_field": None},
            # {"name": "MyJobMagTZ", "url": "https://www.myjobmag.co.tz/jobs", "type": "html", "selector": ".job-item a", "deadline_field": None},
            {"name": "CareerjetTZ", "url": "https://www.careerjet.co.tz/remote-jobs.html", "type": "html", "selector": ".job a", "deadline_field": None},



            {"name": "TruebitsFullStackDev", "url": "https://www.linkedin.com/jobs/view/4279613711", "type": "html", "selector": None, "deadline_field": None},
            {"name": "FlexJavaDev", "url": "https://www.linkedin.com/jobs/view/4281786331", "type": "html", "selector": None, "deadline_field": None},
            {"name": "SaidSalimITOfficer", "url": "http://ats-btr.xyz/#/apply?id=saidsalimbakhresacoltdtransportdivision@itofficer@68cc7b45-677a-493f-b462-1e43855dc169", "type": "html", "selector": None, "deadline_field": None},
            {"name": "NeurotechFullStack", "url": "mailto:kalebu@neurotech.africa", "type": "contact", "deadline_field": None},
            {"name": "LaravelFlutterDev", "url": "mailto:salymdev@gmail.com", "type": "contact", "deadline_field": None},
            {"name": "MilanFiberITSupport", "url": "mailto:hr@mctv.co.tz", "type": "contact", "deadline_field": None},
            {"name": "SnapbyteComputerTeacher", "url": "http://ats-btr.xyz/#/apply?id=snapbyte@computerteacher@ecdcfc87-86ac-4ad9-943c-30d73f8a453c", "type": "html", "selector": None, "deadline_field": None},
            {"name": "DragonflyMobileDev", "url": "http://ats-btr.xyz/#/apply?id=dragonfly@mobiledeveloper@9fc1912d-3062-46d6-8c89-44440a286617", "type": "html", "selector": None, "deadline_field": None},
            {"name": "UNICEFDataInternship", "url": "https://jobs.unicef.org/en-us/job/582618/internship-data-analytics-education-outcomes-fund-eof-hosted-fund-remote-6-months-req582618", "type": "html", "selector": None, "deadline_field": None},
            {"name": "ProgrammerHealthAlerts", "url": "https://www.linkedin.com/jobs/view/4282897634", "type": "html", "selector": None, "deadline_field": None},
       
        ]

    def fetch_api(self, url, source_name, deadline_field=None):
        """Scrape jobs from API endpoint safely"""
        headers = {"User-Agent": "Mozilla/5.0"}
        jobs = []
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                data = data[1:]  # skip metadata for RemoteOK
            for job in data:
                title = job.get("position") or job.get("title")
                company = job.get("company")
                location = job.get("location") or job.get("city")
                link = job.get("url") or job.get("link")
                date_posted = job.get(deadline_field) if deadline_field else None

                if not title or not link:
                    continue

                # Skip expired jobs
                if date_posted:
                    try:
                        deadline = datetime.fromisoformat(date_posted)
                        if deadline < datetime.now():
                            continue
                    except Exception:
                        pass

                jobs.append({
                    "source": source_name,
                    "title": title.strip(),
                    "company": company.strip() if company else None,
                    "location": location.strip() if location else None,
                    "link": link,
                    "date_posted": date_posted
                })
        except requests.RequestException as e:
            print(f"[{source_name}] API request failed: {e}")
        except Exception as e:
            print(f"[{source_name}] Error parsing API data: {e}")
        return jobs

    def fetch_html(self, url, source_name, selector):
        """Scrape jobs from HTML using BeautifulSoup"""
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        jobs = []
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for el in soup.select(selector):
                title = el.text.strip()
                href = el.get("href")
                if title and href:
                    jobs.append({
                        "source": source_name,
                        "title": title,
                        "company": None,
                        "location": None,
                        "link": href,
                        "date_posted": None
                    })
        return jobs

    def get_all_jobs(self):
        """Loop all sources and aggregate jobs"""
        all_jobs = []
        for src in self.sources:
            if src["type"] == "api":
                all_jobs.extend(self.fetch_api(src["url"], src["name"], src.get("deadline_field")))
            elif src["type"] == "html":
                all_jobs.extend(self.fetch_html(src["url"], src["name"], src["selector"]))

        # ✅ Sort newest first by date_posted if available
        return sorted(
            all_jobs, 
            key=lambda x: x["date_posted"] if x["date_posted"] else datetime.now().isoformat(), 
            reverse=True
        )

# ✅ Usage example
if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.get_all_jobs()
    for job in jobs[:20]:  # first 20 jobs
        print(f"{job['source']} | {job['title']} - {job['company']} -> {job['link']}")

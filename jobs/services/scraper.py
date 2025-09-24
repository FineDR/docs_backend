import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from requests.adapters import HTTPAdapter, Retry

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.sources = [
            {"name": "RemoteOK", "url": "https://remoteok.com/api", "type": "api", "deadline_field": None},
            {"name": "JobwebTanzania", "url": "https://www.jobwebtanzania.com/", "type": "html", "selector": ".job-listing a", "deadline_field": None},
            {"name": "GreatTanzaniaJobs", "url": "https://www.greattanzaniajobs.com/jobs/", "type": "html", "selector": ".job-list a", "deadline_field": None},
            {"name": "BrighterMondayTZ", "url": "https://www.brightermonday.co.tz/api/jobs", "type": "api", "deadline_field": "expires_at"},
            {"name": "LinkedInRemoteTZ", "url": "https://www.linkedin.com/jobs-guest/jobs/api/remote-tanzania", "type": "api", "deadline_field": "expirationTimestamp"},
            {"name": "GlassdoorTZ", "url": "https://www.glassdoor.com/Job/tanzania-remote-jobs-SRCH_IL.0,7_IS287_KO8,14.htm", "type": "html", "selector": ".jobCard a", "deadline_field": None},
            {"name": "Indeed", "url": "https://www.indeed.com/jobs?q=remote&l=Tanzania", "type": "html", "selector": ".jobTitle a", "deadline_field": None},
            {"name": "CareerjetTZ", "url": "https://www.careerjet.co.tz/remote-jobs.html", "type": "html", "selector": ".job a", "deadline_field": None},

            # Individual postings / contact emails
            {"name": "TruebitsFullStackDev", "url": "https://www.linkedin.com/jobs/view/4279613711", "type": "html", "selector": None, "deadline_field": None},
            {"name": "FlexJavaDev", "url": "https://www.linkedin.com/jobs/view/4281786331", "type": "html", "selector": None, "deadline_field": None},
            {"name": "SaidSalimITOfficer", "url": "http://ats-btr.xyz/#/apply?id=saidsalimbakhresacoltdtransportdivision@itofficer@68cc7b45-677a-493f-b462-1e43855dc169", "type": "html", "selector": None, "deadline_field": None},
            {"name": "NeurotechFullStack", "url": "mailto:kalebu@neurotech.africa", "type": "contact", "deadline_field": None},
            {"name": "LaravelFlutterDev", "url": "mailto:salymdev@gmail.com", "type": "contact", "deadline_field": None},
            {"name": "MilanFiberITSupport", "url": "mailto:hr@mctv.co.tz", "type": "contact", "deadline_field": None},
        ]

        # Setup a reusable requests session with retries
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    # -----------------------
    # API fetch
    # -----------------------
    def fetch_api(self, url, source_name, deadline_field=None):
        jobs = []
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, list) and source_name == "RemoteOK":
                data = data[1:]  # Skip metadata

            for job in data:
                title = job.get("position") or job.get("title")
                company = job.get("company")
                location = job.get("location") or job.get("city")
                link = job.get("url") or job.get("link")
                date_posted = job.get(deadline_field) if deadline_field else None

                jobs.append({
                    "source": source_name,
                    "title": title.strip() if title else None,
                    "company": company.strip() if company else None,
                    "location": location.strip() if location else None,
                    "link": link,
                    "date_posted": date_posted
                })

        except requests.RequestException as e:
            logger.warning("[%s] API request failed: %s", source_name, e)
        except ValueError as e:
            logger.warning("[%s] JSON parsing error: %s", source_name, e)
        except Exception as e:
            logger.warning("[%s] Unexpected error: %s", source_name, e)

        return jobs

    # -----------------------
    # HTML fetch
    # -----------------------
    def fetch_html(self, url, source_name, selector=None):
        jobs = []

        # Mailto / contact
        if url.startswith("mailto:"):
            jobs.append({
                "source": source_name,
                "title": "Contact",
                "company": None,
                "location": None,
                "link": url,
                "date_posted": None
            })
            return jobs

        # If no selector, treat as single posting
        if not selector:
            jobs.append({
                "source": source_name,
                "title": "Job Posting",
                "company": None,
                "location": None,
                "link": url,
                "date_posted": None
            })
            return jobs

        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for el in soup.select(selector):
                title = el.get_text(strip=True)
                href = el.get("href")
                jobs.append({
                    "source": source_name,
                    "title": title if title else "Job Posting",
                    "company": None,
                    "location": None,
                    "link": href,
                    "date_posted": None
                })
        except requests.RequestException as e:
            logger.warning("[%s] HTML request failed: %s", source_name, e)
        except Exception as e:
            logger.warning("[%s] HTML parsing error: %s", source_name, e)

        return jobs

    # -----------------------
    # Aggregate all jobs
    # -----------------------
    def get_all_jobs(self):
        all_jobs = []
        for src in self.sources:
            try:
                if src["type"] == "api":
                    all_jobs.extend(self.fetch_api(src["url"], src["name"], src.get("deadline_field")))
                elif src["type"] in ["html", "contact"]:
                    all_jobs.extend(self.fetch_html(src["url"], src["name"], src.get("selector")))
            except Exception as e:
                logger.warning("[%s] Failed to fetch jobs: %s", src["name"], e)

        # Sort by date_posted if available, fallback to datetime.min
        def sort_key(job):
            if job["date_posted"]:
                try:
                    return datetime.fromisoformat(job["date_posted"])
                except Exception:
                    return datetime.min
            return datetime.min

        return sorted(all_jobs, key=sort_key, reverse=True)


# -----------------------
# Usage example
# -----------------------
if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.get_all_jobs()
    for job in jobs[:20]:  # First 20 jobs
        print(f"{job['source']} | {job['title']} - {job['company']} -> {job['link']}")

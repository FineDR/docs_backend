# jobs/tasks.py
from celery import shared_task
from .scraper import scrape_job_sites

@shared_task
def scrape_jobs_task():
    return scrape_job_sites()

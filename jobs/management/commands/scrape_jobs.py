# jobs/management/commands/scrape_jobs.py
from django.core.management.base import BaseCommand
from jobs.scraper import scrape_brightermonday

class Command(BaseCommand):
    help = "Scrape jobs from BrighterMonday"

    def handle(self, *args, **kwargs):
        scrape_brightermonday()
        self.stdout.write(self.style.SUCCESS("Jobs scraped successfully"))

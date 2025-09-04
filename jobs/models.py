from django.db import models

class Job(models.Model):
    source = models.CharField(max_length=100)  # e.g., "RemoteOK", "Indeed"
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(unique=True)  # avoids duplicates
    date_posted = models.DateTimeField(blank=True, null=True)  # if API provides post date
    application_deadline = models.DateTimeField(blank=True, null=True)  # optional, for filtering
    scraped_at = models.DateTimeField(auto_now_add=True)  # when we scraped it

    def __str__(self):
        return f"{self.title} at {self.company or 'Unknown'}"

    class Meta:
        ordering = ['-date_posted']  # newest first

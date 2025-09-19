from rest_framework.views import APIView
from rest_framework.response import Response
from .services.scraper import JobScraper

class JobPostListAPIView(APIView):
    def get(self, request):
        scraper = JobScraper()
        # tumia method ya reusable ambayo inashughulikia zote sources
        jobs = scraper.get_all_jobs()
        return Response(jobs)

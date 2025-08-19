from django.contrib import admin
from .models import Education

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "degree",
        "institution",
        "location",
        "start_date",
        "end_date",
        "grade",
    )
    search_fields = ("user__email", "degree", "institution")
    list_filter = ("start_date", "end_date", "institution")
    ordering = ("-start_date",)

from django.contrib import admin
from .models import WorkExperience, Responsibility

# Inline display of responsibilities under each work experience
class ResponsibilityInline(admin.TabularInline):
    model = Responsibility
    extra = 1  # Number of empty forms to display
    min_num = 1  # Require at least 1 responsibility
    verbose_name = "Responsibility"
    verbose_name_plural = "Responsibilities"
    fields = ["value"]

# WorkExperience admin
@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ["job_title", "company", "user", "start_date", "end_date"]
    list_filter = ["user", "start_date", "end_date"]  # Filters on the right sidebar
    search_fields = ["job_title", "company", "user__email"]  # Search bar
    ordering = ["-start_date"]  # Most recent first
    inlines = [ResponsibilityInline]

    fieldsets = (
        ("Work Experience Info", {
            "fields": ("user", "job_title", "company", "location", "start_date", "end_date")
        }),
    )

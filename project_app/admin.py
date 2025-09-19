from django.contrib import admin
from .models import Project, Technology

class TechnologyInline(admin.TabularInline):
    model = Technology
    extra = 1  # Number of empty technology fields when adding a project
    min_num = 1
    verbose_name = "Technology"
    verbose_name_plural = "Technologies"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "link", "created_at", "updated_at")
    search_fields = ("title", "user__email", "technologies__value")
    list_filter = ("created_at", "updated_at")
    inlines = [TechnologyInline]

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("value", "project")
    search_fields = ("value", "project__title")

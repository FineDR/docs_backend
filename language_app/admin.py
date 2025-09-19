from django.contrib import admin
from .models import Language

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("language", "proficiency", "user", "created_at")
    search_fields = ("language", "proficiency", "user__email")

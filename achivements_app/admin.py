from django.contrib import admin
from .models import AchievementProfile, Achievement

@admin.register(AchievementProfile)
class AchievementProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "user")
    search_fields = ("full_name", "email", "user__email")

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("value", "profile")
    search_fields = ("value", "profile__email")

from django.contrib import admin
from .models import CareerObjective

@admin.register(CareerObjective)
class CareerObjectiveAdmin(admin.ModelAdmin):
    list_display = ["user", "career_objective", "created_at"]

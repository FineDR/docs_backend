from django.contrib import admin
from .models import SkillSet, TechnicalSkill, SoftSkill

# Inline for Technical Skills
class TechnicalSkillInline(admin.TabularInline):
    model = TechnicalSkill
    extra = 1  # Number of empty fields to show
    min_num = 0
    verbose_name = "Technical Skill"
    verbose_name_plural = "Technical Skills"

# Inline for Soft Skills
class SoftSkillInline(admin.TabularInline):
    model = SoftSkill
    extra = 1
    min_num = 0
    verbose_name = "Soft Skill"
    verbose_name_plural = "Soft Skills"

# Main SkillSet admin
@admin.register(SkillSet)
class SkillSetAdmin(admin.ModelAdmin):
    list_display = ("user",)  # <-- comma muhimu
    search_fields = ("user__username",)  # <-- comma muhimu
    inlines = [TechnicalSkillInline, SoftSkillInline]

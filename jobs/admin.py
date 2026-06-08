from django.contrib import admin

from .models import Application, CompanyProfile, Interview, Job


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "location")
    search_fields = ("name", "location")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "employment_type",
                    "is_active", "created_at")
    list_filter = ("employment_type", "is_active")
    search_fields = ("title", "company__name")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "candidate", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("job__title", "candidate__username")


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "scheduled_at", "mode", "location_or_link")
    list_filter = ("mode",)
    search_fields = ("application__job__title", "application__candidate__username")

"""URL configuration for the recruitment project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth: register/login/logout/dashboard.
    path("", include("accounts.urls")),
    # Read-only REST API (SPEC §7).
    path("api/", include("api.urls")),
    # Login/logout for the DRF browsable API (testing the gated endpoint).
    path("api-auth/", include("rest_framework.urls")),
    # Core domain (job list at "/", more routes added later).
    path("", include("jobs.urls")),
]

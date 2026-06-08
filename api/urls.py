from django.urls import path

from . import views

# Read-only REST API (SPEC §7).
urlpatterns = [
    path("jobs/", views.JobListAPIView.as_view(), name="api_job_list"),
    path("jobs/<int:pk>/", views.JobDetailAPIView.as_view(), name="api_job_detail"),
    path("applications/", views.ApplicationListAPIView.as_view(), name="api_application_list"),
]

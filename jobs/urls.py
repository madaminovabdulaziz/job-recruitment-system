from django.urls import path

from . import views

# Named routes for the jobs app.
urlpatterns = [
    # Public
    path("", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    # Candidate
    path("candidate/applications/", views.my_applications, name="my_applications"),
    path("jobs/<int:pk>/apply/", views.apply_to_job, name="apply"),
    path("applications/<int:pk>/withdraw/", views.withdraw_application, name="withdraw"),
    # Employer: dashboard + job CRUD
    path("employer/jobs/", views.employer_jobs, name="employer_jobs"),
    path("employer/jobs/new/", views.job_create, name="job_create"),
    path("employer/jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("employer/jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    # Employer: applicant management
    path("employer/jobs/<int:pk>/applicants/", views.job_applicants, name="job_applicants"),
    path("applications/<int:pk>/status/", views.update_status, name="update_status"),
    path("applications/<int:pk>/interview/", views.schedule_interview, name="schedule_interview"),
]

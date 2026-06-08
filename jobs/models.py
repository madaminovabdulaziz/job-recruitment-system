from django.conf import settings
from django.db import models


class CompanyProfile(models.Model):
    """An employer's company profile. One profile per employer user (SPEC §5.2)."""

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    """A vacancy posted by a company (SPEC §5.3)."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full time"
        PART_TIME = "part_time", "Part time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices
    )
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    """A candidate's application to a job. One application per job per candidate
    (SPEC §5.4)."""

    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        UNDER_REVIEW = "under_review", "Under review"
        INTERVIEW = "interview", "Interview"
        OFFERED = "offered", "Offered"
        REJECTED = "rejected", "Rejected"

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    cover_letter = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPLIED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One application per job per candidate (SPEC §5.4).
        unique_together = ("job", "candidate")

    def __str__(self):
        return f"{self.candidate} → {self.job}"


class Interview(models.Model):
    """An interview scheduled for an application. One interview per application
    (SPEC §5.5)."""

    class Mode(models.TextChoices):
        ONSITE = "onsite", "Onsite"
        ONLINE = "online", "Online"

    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    mode = models.CharField(max_length=10, choices=Mode.choices)
    location_or_link = models.CharField(max_length=300)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Interview for {self.application}"

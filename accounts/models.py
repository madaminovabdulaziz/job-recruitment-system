from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model. Every user is either a candidate or an employer,
    chosen at registration (SPEC §5.1). Extending AbstractUser keeps Django's
    built-in username/email/password/auth machinery."""

    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        EMPLOYER = "employer", "Employer"

    role = models.CharField(max_length=10, choices=Role.choices)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

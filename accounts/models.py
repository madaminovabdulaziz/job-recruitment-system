from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        EMPLOYER = "employer", "Employer"

    role = models.CharField(max_length=10, choices=Role.choices)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

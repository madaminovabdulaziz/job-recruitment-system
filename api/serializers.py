from rest_framework import serializers

from jobs.models import Application, Job


class JobListSerializer(serializers.ModelSerializer):
    """Compact job representation for the list endpoint (SPEC §7):
    id, title, company name, location, type, created_at."""

    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company_name",
            "location",
            "employment_type",
            "created_at",
        ]


class JobDetailSerializer(JobListSerializer):
    """Fuller job representation for the detail endpoint — adds description,
    salary range and active flag on top of the list fields."""

    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + [
            "description",
            "salary_min",
            "salary_max",
            "is_active",
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    """A candidate's own application (SPEC §7). Includes the job title and
    company so the response is readable without extra lookups."""

    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company.name", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "status",
            "cover_letter",
            "created_at",
        ]

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from jobs.models import Application, Job

from .serializers import (
    ApplicationSerializer,
    JobDetailSerializer,
    JobListSerializer,
)


class JobListAPIView(generics.ListAPIView):
    """GET /api/jobs/ — list active jobs. Public, read-only (SPEC §7)."""

    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    queryset = Job.objects.filter(is_active=True).order_by("-created_at")


class JobDetailAPIView(generics.RetrieveAPIView):
    """GET /api/jobs/<id>/ — single job detail. Public, read-only.
    Returns 404 for an unknown id."""

    serializer_class = JobDetailSerializer
    permission_classes = [AllowAny]
    queryset = Job.objects.all()


class ApplicationListAPIView(generics.ListAPIView):
    """GET /api/applications/ — the logged-in user's own applications only.
    Permission-gated: anonymous requests are rejected (SPEC §7)."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Scope to the requesting user so no one sees another user's applications.
        return (
            Application.objects.filter(candidate=self.request.user)
            .select_related("job", "job__company")
            .order_by("-created_at")
        )

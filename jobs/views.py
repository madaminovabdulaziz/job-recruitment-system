from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import ApplicationForm, InterviewForm, JobForm, StatusForm
from .models import Application, Interview, Job


# --- Public job browsing (SPEC §6) ---

def job_list(request):
    """Public landing page: active jobs as cards, with a simple search on
    title/location via the `q` query parameter. Public access."""
    q = request.GET.get("q", "").strip()
    jobs = (
        Job.objects.filter(is_active=True)
        .select_related("company")
        .order_by("-created_at")
    )
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(location__icontains=q))
    return render(request, "jobs/job_list.html", {"jobs": jobs, "q": q})


def job_detail(request, pk):
    """Public detail page for a single job. Shows an Apply button to candidates
    who haven't applied yet. Public access."""
    job = get_object_or_404(Job, pk=pk)
    already_applied = (
        request.user.is_authenticated
        and request.user.role == User.Role.CANDIDATE
        and Application.objects.filter(job=job, candidate=request.user).exists()
    )
    return render(
        request,
        "jobs/job_detail.html",
        {"job": job, "already_applied": already_applied},
    )


# --- Ownership helpers (SPEC §8) ---

def _own_jobs(user):
    """Jobs owned by this employer. Scoping every employer query through this
    means an employer can only ever see/edit/delete their own jobs."""
    return Job.objects.filter(company__owner=user)


def _employer_applications(user):
    """Applications to this employer's jobs — used to gate status/interview
    actions so an employer can only act on applications to their own jobs."""
    return Application.objects.filter(job__company__owner=user)


# --- Candidate: apply / withdraw / dashboard (candidate-only) ---

@role_required(User.Role.CANDIDATE)
def apply_to_job(request, pk):
    """Apply to an active job. One application per job per candidate — a
    duplicate is blocked here (and by the DB unique constraint). Candidate-only."""
    job = get_object_or_404(Job, pk=pk, is_active=True)

    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.info(request, "You have already applied to this job.")
        return redirect("job_detail", pk=job.pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.save()
            messages.success(request, f"Applied to '{job.title}'.")
            return redirect("my_applications")
    else:
        form = ApplicationForm()

    return render(request, "jobs/apply.html", {"form": form, "job": job})


@role_required(User.Role.CANDIDATE)
def withdraw_application(request, pk):
    """Withdraw (delete) one of the candidate's own applications. Candidate-only
    + ownership-checked. GET shows a confirm page; POST performs the withdrawal."""
    application = get_object_or_404(Application, pk=pk, candidate=request.user)

    if request.method == "POST":
        title = application.job.title
        application.delete()
        messages.success(request, f"Withdrew your application to '{title}'.")
        return redirect("my_applications")

    return render(request, "jobs/withdraw_confirm.html", {"application": application})


@role_required(User.Role.CANDIDATE)
def my_applications(request):
    """Candidate dashboard: the candidate's own applications with status (and
    interview details if scheduled), plus a small summary. Candidate-only."""
    applications = (
        Application.objects.filter(candidate=request.user)
        .select_related("job", "job__company")
        .order_by("-created_at")
    )
    summary = {
        "total": applications.count(),
        "interviews": applications.filter(status=Application.Status.INTERVIEW).count(),
        "offers": applications.filter(status=Application.Status.OFFERED).count(),
    }
    return render(
        request,
        "jobs/my_applications.html",
        {"applications": applications, "summary": summary},
    )


# --- Employer dashboard + job CRUD (employer-only) ---

@role_required(User.Role.EMPLOYER)
def employer_jobs(request):
    """Employer dashboard: the employer's own jobs with applicant counts, plus a
    summary of totals. Employer-only."""
    jobs = (
        _own_jobs(request.user)
        .annotate(num_applicants=Count("application"))
        .order_by("-created_at")
    )
    summary = {
        "total_jobs": len(jobs),
        "active_jobs": sum(1 for j in jobs if j.is_active),
        "total_applicants": sum(j.num_applicants for j in jobs),
    }
    return render(
        request, "jobs/employer_jobs.html", {"jobs": jobs, "summary": summary}
    )


@role_required(User.Role.EMPLOYER)
def job_create(request):
    """Create a new job for the logged-in employer's company. Employer-only."""
    profile = getattr(request.user, "companyprofile", None)
    if profile is None:
        messages.error(request, "You need a company profile before posting jobs.")
        return redirect("employer_jobs")

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = profile  # owner set server-side, never from the form
            job.save()
            messages.success(request, f"Job '{job.title}' posted.")
            return redirect("employer_jobs")
    else:
        form = JobForm()

    return render(request, "jobs/job_form.html", {"form": form, "heading": "Post a Job"})


@role_required(User.Role.EMPLOYER)
def job_edit(request, pk):
    """Edit one of the employer's own jobs. Employer-only + ownership-checked."""
    job = get_object_or_404(_own_jobs(request.user), pk=pk)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated.")
            return redirect("employer_jobs")
    else:
        form = JobForm(instance=job)

    return render(request, "jobs/job_form.html", {"form": form, "heading": "Edit Job"})


@role_required(User.Role.EMPLOYER)
def job_delete(request, pk):
    """Delete one of the employer's own jobs. Employer-only + ownership-checked.
    GET shows a confirm page (no-JS fallback); POST performs the delete."""
    job = get_object_or_404(_own_jobs(request.user), pk=pk)

    if request.method == "POST":
        title = job.title
        job.delete()
        messages.success(request, f"Job '{title}' deleted.")
        return redirect("employer_jobs")

    return render(request, "jobs/job_confirm_delete.html", {"job": job})


# --- Employer: applicant management (employer-only + ownership) ---

@role_required(User.Role.EMPLOYER)
def job_applicants(request, pk):
    """List the applicants for one of the employer's own jobs, each with a status
    form and interview state. Employer-only + ownership-checked."""
    job = get_object_or_404(_own_jobs(request.user), pk=pk)
    applications = job.application_set.select_related("candidate").order_by("-created_at")
    # Pair each application with a bound status form for inline editing.
    rows = [(app, StatusForm(instance=app)) for app in applications]
    return render(request, "jobs/job_applicants.html", {"job": job, "rows": rows})


@role_required(User.Role.EMPLOYER)
def update_status(request, pk):
    """Change the status of an application to one of the employer's own jobs.
    Employer-only + ownership-checked."""
    application = get_object_or_404(_employer_applications(request.user), pk=pk)

    if request.method == "POST":
        form = StatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated.")
        else:
            messages.error(request, "Invalid status.")

    return redirect("job_applicants", pk=application.job.pk)


@role_required(User.Role.EMPLOYER)
def schedule_interview(request, pk):
    """Create or edit the interview for an application to one of the employer's
    own jobs (one interview per application). Employer-only + ownership-checked."""
    application = get_object_or_404(_employer_applications(request.user), pk=pk)

    # Interview is a OneToOne; it may not exist yet.
    try:
        interview = application.interview
    except Interview.DoesNotExist:
        interview = None

    if request.method == "POST":
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
            messages.success(request, "Interview saved.")
            return redirect("job_applicants", pk=application.job.pk)
    else:
        form = InterviewForm(instance=interview)

    return render(
        request,
        "jobs/interview_form.html",
        {"form": form, "application": application, "interview": interview},
    )

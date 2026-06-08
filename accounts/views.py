from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from jobs.models import CompanyProfile

from .forms import RegisterForm
from .models import User


def register(request):
    """Register a new account and choose a role (SPEC §2, §8).

    Anyone (anonymous) can register. Employers also get a CompanyProfile
    created from the company fields on the form. On success the user is logged
    in and sent to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # saves username, email, role, hashed password
            if user.role == User.Role.EMPLOYER:
                CompanyProfile.objects.create(
                    owner=user,
                    name=form.cleaned_data["company_name"],
                    description=form.cleaned_data["company_description"],
                    location=form.cleaned_data["company_location"],
                    website=form.cleaned_data["company_website"],
                )
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    """Send a logged-in user to the right dashboard for their role (SPEC §6)."""
    if request.user.role == User.Role.EMPLOYER:
        return redirect("employer_jobs")
    return redirect("my_applications")

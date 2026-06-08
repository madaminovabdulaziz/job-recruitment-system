from django import forms

from .models import Application, Interview, Job


def _bootstrap(fields):
    """Apply Bootstrap classes to a form's widgets based on their type.
    Keeps each form's __init__ short and consistent."""
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        else:
            widget.attrs.setdefault("class", "form-control")


class JobForm(forms.ModelForm):
    """Create/update form for a Job (SPEC §4 CRUD). The owning company is set
    in the view from the logged-in employer, so it isn't a form field."""

    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "location",
            "employment_type",
            "salary_min",
            "salary_max",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)


class ApplicationForm(forms.ModelForm):
    """A candidate's application to a job — just the cover letter. The job and
    candidate are set in the view (SPEC §5.4)."""

    class Meta:
        model = Application
        fields = ["cover_letter"]
        widgets = {"cover_letter": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)


class StatusForm(forms.ModelForm):
    """Employer-side form to change an application's status (SPEC §6)."""

    class Meta:
        model = Application
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)
        self.fields["status"].widget.attrs["class"] = "form-select form-select-sm"


class InterviewForm(forms.ModelForm):
    """Create/edit the interview for an application (SPEC §5.5, §6)."""

    class Meta:
        model = Interview
        fields = ["scheduled_at", "mode", "location_or_link", "notes"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Accept the value the datetime-local input sends back.
        self.fields["scheduled_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        _bootstrap(self.fields)

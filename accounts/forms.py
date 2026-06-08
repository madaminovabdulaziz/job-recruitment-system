from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    """Registration form: standard username/password plus a required role.

    When the user picks "employer", the company fields become required so we
    can create their CompanyProfile in the same step.
    """

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.RadioSelect)

    # Company fields — only used (and required) when role == employer.
    company_name = forms.CharField(max_length=200, required=False)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
    company_location = forms.CharField(max_length=200, required=False)
    company_website = forms.URLField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # role/email are saved automatically because they're listed here.
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap styling to every widget; role uses radio buttons.
        for name, field in self.fields.items():
            css = "form-check-input" if name == "role" else "form-control"
            field.widget.attrs.setdefault("class", css)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("role") == User.Role.EMPLOYER:
            # Employers must supply enough to build a CompanyProfile.
            for field in ("company_name", "company_description", "company_location"):
                if not cleaned.get(field):
                    self.add_error(field, "This field is required for employers.")
        return cleaned

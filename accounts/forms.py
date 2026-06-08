from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.RadioSelect)

    # Company fields — only used (and required) when role == employer.
    company_name = forms.CharField(max_length=200, required=False)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
    company_location = forms.CharField(max_length=200, required=False)
    company_website = forms.URLField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-check-input" if name == "role" else "form-control"
            field.widget.attrs.setdefault("class", css)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("role") == User.Role.EMPLOYER:
            for field in ("company_name", "company_description", "company_location"):
                if not cleaned.get(field):
                    self.add_error(field, "This field is required for employers.")
        return cleaned

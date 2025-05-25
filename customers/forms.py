from django import forms
from .models import Member
from branches.models import Branch


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name", "phone", "email", "address", "status", "branch", "notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter full name",
                    "required": "true",
                    "autofocus": "true",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+1234567890",
                    "required": "true",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email address",
                    "required": "true",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter address",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select", "required": "true"}),
            "branch": forms.Select(attrs={"class": "form-select", "required": "true"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter any additional notes",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Filter branches based on user's role
        if self.user:
            if self.user.role == "admin":
                # Admin can see all branches
                self.fields["branch"].queryset = Branch.objects.all()
            else:
                # Other users can only see their branch
                self.fields["branch"].queryset = Branch.objects.filter(
                    id=self.user.branch.id
                )
                # If editing, don't allow changing branch
                if self.instance.pk:
                    self.fields["branch"].disabled = True

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.startswith("+"):
            phone = "+" + phone
        return phone

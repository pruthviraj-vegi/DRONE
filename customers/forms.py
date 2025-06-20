from django import forms
from .models import Member
from branches.models import Branch


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name", "phone", "address", "status", "branches", "notes"]
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
                    "placeholder": "1234567890",
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
            "branches": forms.SelectMultiple(
                attrs={"class": "form-select", "required": "true"}
            ),
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
                self.fields["branches"].queryset = Branch.objects.all()
            else:
                # Other users can only see their branch
                self.fields["branches"].queryset = Branch.objects.filter(
                    id=self.user.branch.id
                )
                # If editing, don't allow changing branches
                if self.instance.pk:
                    self.fields["branches"].disabled = True

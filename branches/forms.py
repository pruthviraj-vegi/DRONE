from django import forms
from .models import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = [
            "name",
            "code",
            "type",
            "parent",
            "address",
            "phone",
            "email",
            "is_active",
        ]
        widgets = {
            "type": forms.Select(attrs={"class": "form-select"}),
            "parent": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Short Code for Branch",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show main branches as parent options for sub branches
        if self.instance and self.instance.pk:
            self.fields["parent"].queryset = Branch.objects.exclude(pk=self.instance.pk)
        else:
            self.fields["parent"].queryset = Branch.objects.all()
        self.fields["parent"].required = False
        self.fields["is_active"].required = False

    def clean(self):
        cleaned_data = super().clean()
        branch_type = cleaned_data.get("type")
        parent = cleaned_data.get("parent")

        if branch_type == "main":
            # Main branches should not have a parent
            cleaned_data["parent"] = None
        elif branch_type == "sub":
            # Sub branches must have a parent, and it must be a main branch
            if not parent:
                self.add_error(
                    "parent", "Sub branches must have a main branch as parent."
                )
            elif parent.type != "main":
                self.add_error("parent", "Parent branch must be a main branch.")
        return cleaned_data

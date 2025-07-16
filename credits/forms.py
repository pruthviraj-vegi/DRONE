# credits/forms.py
from django import forms
from .models import Credit
from customers.models import Member


class CreditForm(forms.ModelForm):
    def __init__(self, *args, include_member=True, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if not include_member:
            self.fields.pop("member", None)

        if include_member and "member" in self.fields and self.user:
            if self.user.role == "admin":
                self.fields["member"].queryset = Member.objects.filter(status="active")
            else:
                self.fields["member"].queryset = Member.objects.filter(
                    branches=self.user.branch,
                    status="active",
                )

    class Meta:
        model = Credit
        fields = ["member", "paid", "amount", "notes", "created_at"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
            "paid": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "created_at": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        return amount

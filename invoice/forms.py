from django import forms
from customers.models import Member
from invoice.models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "customer",
            "invoice_type",
            "payment_mode",
            "total_amount",
            "advance_amount",
            "notes",
        ]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
            "invoice_type": forms.Select(attrs={"class": "form-select"}),
            "payment_mode": forms.Select(attrs={"class": "form-select"}),
            "total_amount": forms.TextInput(
                attrs={"class": "form-control", "readonly": True}
            ),
            "advance_amount": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.role == "admin":
                self.fields["customer"].queryset = Member.objects.filter(
                    status="active"
                )
            else:
                self.fields["customer"].queryset = Member.objects.filter(
                    branches=self.user.branch,
                    status="active",
                )

    def clean(self):
        cleaned_data = super().clean()
        advance_amount = cleaned_data.get("advance_amount")
        total_amount = cleaned_data.get("total_amount")
        invoice_type = cleaned_data.get("invoice_type")

        if int(total_amount) <= 0:
            raise forms.ValidationError("Amount must be greater than 0")

        # Only validate if all fields are present and valid
        if advance_amount is not None and total_amount is not None:
            if invoice_type:
                cleaned_data["advance_amount"] = 0
            else:
                if advance_amount > total_amount:
                    raise forms.ValidationError(
                        "Advance amount cannot be greater than total amount"
                    )
        return cleaned_data

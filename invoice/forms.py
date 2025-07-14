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

        self.fields["customer"].widget.attrs["class"] = "form-select"
        self.fields["invoice_type"].widget.attrs["class"] = "form-select"
        self.fields["total_amount"].widget.attrs["class"] = "form-control"
        self.fields["payment_mode"].widget.attrs["class"] = "form-select"
        self.fields["notes"].widget.attrs["class"] = "form-control"
        self.fields["advance_amount"].widget.attrs["class"] = "form-control"

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

    def clean_amount(self):
        amount = self.cleaned_data["total_amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        return amount

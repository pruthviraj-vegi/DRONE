from django import forms
from customers.models import Member
from invoice.models import Invoice
from decimal import Decimal


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "customer",
            "invoice_type",
            "payment_mode",
            "total_amount",
            "advance_amount",
            "discount_amount",
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
            "discount_amount": forms.TextInput(attrs={"class": "form-control"}),
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

    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get("discount_amount")
        if discount_amount < 0:
            raise forms.ValidationError("Discount amount cannot be negative")
        return discount_amount

    def clean_advance_amount(self):
        advance_amount = self.cleaned_data.get("advance_amount")
        if advance_amount < 0:
            raise forms.ValidationError("Advance amount cannot be negative")
        return advance_amount

    def clean_total_amount(self):
        total_amount = self.cleaned_data.get("total_amount")
        if total_amount < 0:
            raise forms.ValidationError("Total amount cannot be negative")
        return total_amount

    def clean_invoice_type(self):
        invoice_type = self.cleaned_data.get("invoice_type")
        if invoice_type is None:
            raise forms.ValidationError("Invoice type is required")
        return invoice_type


    def clean(self):
        cleaned_data = super().clean()
        advance_amount = cleaned_data.get("advance_amount")
        total_amount = cleaned_data.get("total_amount")
        invoice_type = cleaned_data.get("invoice_type")

        if int(total_amount) <= 0:
            raise forms.ValidationError("Amount must be greater than 0")

        # Set advance amount to 0 for cash invoice type (invoice_type = True)
        if invoice_type:
            cleaned_data["advance_amount"] = Decimal(0)
        else:
            # For credit invoices, validate advance amount
            if advance_amount is not None and total_amount is not None:
                if advance_amount > total_amount:
                    raise forms.ValidationError(
                        "Advance amount cannot be greater than total amount"
                    )
        return cleaned_data

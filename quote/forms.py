from django import forms
from .models import QuoteInventory, QuoteMember, QuoteSession, QuoteItem
from django.forms import modelformset_factory, formset_factory


class QuoteMemberForm(forms.ModelForm):
    class Meta:
        model = QuoteMember
        fields = ["name", "phone", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }


class QuoteInventoryForm(forms.ModelForm):
    class Meta:
        model = QuoteInventory
        fields = ["name", "price", "discount", "tax", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "discount": forms.NumberInput(attrs={"class": "form-control"}),
            "tax": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class QuoteSessionForm(forms.ModelForm):
    class Meta:
        model = QuoteSession
        fields = ["customer", "status"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, show_status=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not show_status:
            self.fields.pop("status")

    def save(self, commit=True):
        self.instance.status = "processing"
        return super().save(commit)


class QuoteItemAddForm(forms.Form):
    inventory_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=10,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Quantity"}
        ),
    )
    price = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Price"}
        ),
    )

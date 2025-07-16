from django import forms
from .models import QuoteInventory, QuoteMember, QuoteSession, QuoteItem
from django.forms import modelformset_factory, formset_factory


class QuoteMemberForm(forms.ModelForm):
    class Meta:
        model = QuoteMember
        fields = ["name", "phone", "address"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Name",
                    "autofocus": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address"}
            ),
        }


class QuoteInventoryForm(forms.ModelForm):
    class Meta:
        model = QuoteInventory
        fields = ["name", "price", "discount", "tax", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Name",
                    "autofocus": True,
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Price"}
            ),
            "discount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Discount"}
            ),
            "tax": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Tax"}
            ),
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

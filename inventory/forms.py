from django import forms
from .models import Inventory, StockTransaction


class InventoryCreateForm(forms.ModelForm):

    class Meta:
        model = Inventory

        exclude = [
            "barcode",
            "created_at",
            "updated_at",
            "created_by",
            "available_quantity",
            "branch",
        ]

        widgets = {
            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Company Name",
                    "autofocus": True,
                }
            ),
            "part_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Part Name"}
            ),
            "part_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Part Number"}
            ),
            "minimum_quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Minimum Quantity"}
            ),
            "uom": forms.Select(attrs={"class": "form-select"}),
            "barcode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Barcode"}
            ),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Notes"}
            ),
            "purchased_price": forms.NumberInput(attrs={"class": "form-control"}),
            "selling_price": forms.NumberInput(attrs={"class": "form-control"}),
            "discount": forms.NumberInput(attrs={"class": "form-control"}),
            "minimum_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "gst": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.order_fields(
            [
                "company_name",
                "part_name",
                "part_number",
                "minimum_quantity",
                "quantity",
                "uom",
                "purchased_price",
                "selling_price",
                "discount",
                "gst",
                "notes",
                "is_active",
            ]
        )


class StockTransactionForm(forms.ModelForm):

    class Meta:
        model = StockTransaction
        fields = ["transaction_type", "quantity", "reference_number", "notes"]
        widgets = {
            "transaction_type": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove 'initial' from the dropdown choices
        choices = [
            c for c in self.fields["transaction_type"].choices if c[0] != "initial"
        ]
        self.fields["transaction_type"].choices = choices

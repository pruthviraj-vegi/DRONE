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
                    "placeholder": "Enter company name (e.g., Toyota, Honda)",
                    "autofocus": True,
                }
            ),
            "part_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter part name (e.g., Oil Filter, Brake Pad)",
                }
            ),
            "part_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter part number (optional)",
                }
            ),
            "minimum_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Minimum stock level",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "uom": forms.Select(attrs={"class": "form-select"}),
            "barcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Barcode (auto-generated if empty)",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Initial quantity",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes about this item",
                }
            ),
            "purchased_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Cost price",
                }
            ),
            "selling_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Selling price",
                }
            ),
            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "100",
                    "step": "0.01",
                    "placeholder": "Discount percentage",
                }
            ),
            "gst": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "100",
                    "step": "0.01",
                    "placeholder": "GST percentage",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        help_texts = {
            "company_name": "The manufacturer or supplier company name",
            "part_name": "The name of the part or item",
            "part_number": "Optional part number for reference",
            "minimum_quantity": "Alert will be shown when stock falls below this level",
            "quantity": "Initial stock quantity",
            "purchased_price": "Cost price per unit",
            "selling_price": "Selling price per unit",
            "discount": "Discount percentage (0-100)",
            "gst": "GST percentage (0-100)",
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

    def clean(self):
        cleaned_data = super().clean()
        purchased_price = cleaned_data.get("purchased_price")
        selling_price = cleaned_data.get("selling_price")

        if purchased_price and selling_price and purchased_price > selling_price:
            raise forms.ValidationError(
                "Selling price should be greater than or equal to purchased price."
            )

        return cleaned_data


class StockTransactionForm(forms.ModelForm):

    class Meta:
        model = StockTransaction
        fields = ["transaction_type", "quantity", "reference_number", "notes"]
        widgets = {
            "transaction_type": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "Enter quantity",
                }
            ),
            "reference_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "PO/SO number or reference",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Transaction notes",
                }
            ),
        }

        help_texts = {
            "transaction_type": "Type of stock movement",
            "quantity": "Quantity to add or remove",
            "reference_number": "Purchase order, sales order, or other reference number",
            "notes": "Additional details about this transaction",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove 'initial' from the dropdown choices
        choices = [
            c for c in self.fields["transaction_type"].choices if c[0] != "initial"
        ]
        self.fields["transaction_type"].choices = choices

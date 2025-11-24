from django import forms
from django.forms import inlineformset_factory
from .models import Inventory, StockTransaction, ProductAssembly, AssemblyComponent


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


class ProductAssemblyForm(forms.ModelForm):
    class Meta:
        model = ProductAssembly
        exclude = [
            "barcode",
            "created_at",
            "updated_at",
            "created_by",
            "branch",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter assembly name (e.g., Drone Assembly XY)",
                    "autofocus": True,
                }
            ),
            "sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter SKU (e.g., DRONE-XY-001)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Assembly description",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes about this assembly",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        help_texts = {
            "name": "The name of the product assembly",
            "sku": "Stock Keeping Unit - unique identifier for the assembly",
            "description": "Detailed description of the assembly",
            "notes": "Additional notes or instructions",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["name", "sku", "description", "notes", "is_active"])


class AssemblyComponentForm(forms.ModelForm):
    class Meta:
        model = AssemblyComponent
        fields = ["inventory_item", "quantity_required", "selling_price", "notes"]
        widgets = {
            "inventory_item": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "quantity_required": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "Quantity needed",
                }
            ),
            "selling_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Selling price for this component",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Component notes (optional)",
                }
            ),
        }

        help_texts = {
            "inventory_item": "Select the inventory item to include in this assembly",
            "quantity_required": "How many units of this item are needed per assembly",
            "selling_price": "Selling price for this component when sold as part of the assembly (leave 0 to use inventory item price)",
            "notes": "Optional notes about this component",
        }


# Inline formset for assembly components
AssemblyComponentFormSet = inlineformset_factory(
    ProductAssembly,
    AssemblyComponent,
    form=AssemblyComponentForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

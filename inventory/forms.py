from django import forms
from .models import Inventory, StockTransaction
from suppliers.models import Supplier


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            "supplier",
            "company_name",
            "part_name",
            "part_number",
            "purchased_price",
            "selling_price",
            "discount",
            "quantity",
            "minimum_quantity",
            "description",
            "is_active",
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
                attrs={
                    "class": "form-control",
                    "placeholder": "Part Name",
                }
            ),
            "part_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Part Number"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Description Of the product",
                }
            ),
            "purchased_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Purchased Price"}
            ),
            "selling_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Selling Price"}
            ),
            "discount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Discount"}
            ),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Quantity"}
            ),
            "minimum_quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Minimum Quantity"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Supplier.objects.filter(is_active=True)
        # Hide is_active on create
        if not self.instance.pk:
            self.fields.pop("is_active")
            # self.fields["is_active"].widget = forms.HiddenInput()


TRANSACTION_TYPE_CHOICES = [
    ("purchase", "Purchase"),
    ("sale", "Sale"),
    ("adjustment", "Adjustment"),
    ("return", "Return"),
    ("damage", "Damage/Loss"),
]


class UpdateStockForm(forms.Form):
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
        label="Transaction Type",
    )
    quantity_change = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "+/- Quantity"}
        ),
        required=True,
        label="Quantity Change",
    )
    reference_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g., PO-123, SO-456"}
        ),
        label="Reference Number",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Add any additional information about this transaction",
            }
        ),
        label="Notes",
    )


class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ["transaction_type", "quantity_change", "reference_number", "notes"]
        widgets = {
            "transaction_type": forms.Select(attrs={"class": "form-select"}),
            "quantity_change": forms.NumberInput(attrs={"class": "form-control"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

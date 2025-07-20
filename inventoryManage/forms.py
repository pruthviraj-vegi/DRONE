from django import forms
from branches.models import Branch
from inventory.models import Inventory
from inventoryManage.models import BranchInventory


class BranchInventoryTransferForm(forms.Form):
    to_branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(), label="To Branch"  # Set default to none
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, user_branch=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_branch:
            self.fields["to_branch"].queryset = Branch.objects.filter(
                is_active=True
            ).exclude(id=user_branch.id)
        else:
            self.fields["to_branch"].queryset = Branch.objects.filter(is_active=True)


class BranchInventoryTransferItemForm(forms.Form):
    inventory = forms.ModelChoiceField(
        queryset=Inventory.objects.none(), label="Inventory Item"
    )
    quantity = forms.DecimalField(min_value=1, label="Quantity")

    def __init__(self, *args, user_branch=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_branch:
            # First, try to get inventory items that exist in the user's branch
            branch_inventory_items = BranchInventory.objects.filter(
                branch=user_branch
            ).values_list("inventory_id", flat=True)

            if branch_inventory_items.exists():
                # If there are BranchInventory records, filter by them
                self.fields["inventory"].queryset = Inventory.objects.filter(
                    id__in=branch_inventory_items, is_active=True
                )
            else:
                # If no BranchInventory records exist, show all inventory items from the user's branch
                self.fields["inventory"].queryset = Inventory.objects.filter(
                    branch=user_branch, is_active=True
                )
        else:
            self.fields["inventory"].queryset = Inventory.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        inventory = cleaned_data.get("inventory")
        quantity = cleaned_data.get("quantity")

        if inventory and quantity:
            # Get the branch inventory for this item in the user's branch
            try:
                # We need to get the user's branch from the form instance
                # This is a bit tricky with formset, so we'll handle this in the view
                pass
            except Exception as e:
                raise forms.ValidationError(f"Error validating inventory: {str(e)}")

        return cleaned_data


def create_transfer_item_formset(user_branch):
    """Create a formset factory for transfer items with user branch filtering"""

    class TransferItemForm(BranchInventoryTransferItemForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, user_branch=user_branch, **kwargs)

    from django.forms import formset_factory

    return formset_factory(TransferItemForm, extra=1)

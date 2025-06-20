from django import forms
from branches.models import Branch
from inventory.models import Inventory


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
        queryset=Inventory.objects.filter(is_active=True), label="Inventory Item"
    )
    quantity = forms.IntegerField(min_value=1, label="Quantity")

from django.db import models
from django.utils import timezone
from django.conf import settings
from inventory.models import Inventory
from branches.models import Branch
from django.contrib.auth import get_user_model

# Create your models here.


class TransactionDetail(models.Model):
    name = models.CharField(max_length=255)
    from_branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="from_transaction_details"
    )
    to_branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="to_transaction_details"
    )
    transfered_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.name:
            self.name = (
                f"{self.from_branch.code}-{str(self.id).zfill(4)}-{self.to_branch.code}"
            )
            super().save(update_fields=["name"])


class BranchInventory(models.Model):
    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="branch_assignments"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="inventory_assignments"
    )
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.inventory.part_name} - {self.branch.name}"


class BranchInventoryTransaction(models.Model):

    branch_inventory = models.ForeignKey(
        BranchInventory, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_detail = models.ForeignKey(
        TransactionDetail, on_delete=models.CASCADE, related_name="transactions_detail"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=[("forward", "Forward"), ("update", "Update"), ("return", "Return")],
    )
    quantity_change = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.branch_inventory.inventory.part_name} - {self.branch_inventory.branch.name}"

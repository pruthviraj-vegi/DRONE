from django.db import models
from django.utils import timezone
from inventory.models import Inventory
from branches.models import Branch
from django.contrib.auth import get_user_model
from django.db.models import Sum

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
        Inventory, on_delete=models.CASCADE, related_name="branch_inventory_inventory"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="inventory_assignments"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.inventory.part_name} - {self.branch.name}"

    def actual_quantity(self):
        """
        Calculate actual available quantity by subtracting session items from available_quantity
        """
        # Get total quantity from active billing sessions for this inventory and branch
        session_items_total = (
            self.inventory.billing_session_items.filter(
                session__is_active=True, session__user__branch=self.branch
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        # Actual available = available_quantity - session_items_total
        actual_available = self.available_quantity - session_items_total
        return max(actual_available, 0)  # Ensure we don't return negative values

    def is_quantity_available(self, requested_quantity, exclude_session_item=None):
        """
        Check if requested quantity is available, optionally excluding a specific session item
        """
        actual_available = self.actual_quantity()

        # If excluding a specific session item, add its quantity back to available
        if exclude_session_item:
            actual_available += exclude_session_item.quantity

        return actual_available >= requested_quantity


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
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.branch_inventory.inventory.part_name} - {self.branch_inventory.branch.name}"

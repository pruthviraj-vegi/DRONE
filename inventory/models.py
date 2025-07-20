from django.db import models
from django.utils import timezone
from django.conf import settings
from suppliers.models import Supplier
from django.db.models import Sum
import random
import string
from base.stringProcess import StringProcessor
from branches.models import Branch


class Inventory(models.Model):
    UOM_CHOICES = [
        ("PCS", "Pieces"),
        ("LIT", "Liters"),
        ("BOX", "Boxes"),
        ("SET", "Sets"),
        ("PAK", "Packs"),
        ("BAG", "Bags"),
    ]

    company_name = models.CharField(max_length=100)
    part_name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    uom = models.CharField(max_length=100, default="PCS", choices=UOM_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventories_created_by",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="inventories_branch",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            for _ in range(5):
                barcode = "".join(random.choices(string.digits, k=6))
                if not Inventory.objects.filter(barcode=barcode).exists():
                    self.barcode = barcode
                    break

        self.company_name = StringProcessor(self.company_name).title
        self.part_name = StringProcessor(self.part_name).title
        self.part_number = StringProcessor(self.part_number).uppercase
        self.notes = StringProcessor(self.notes).title
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.barcode or 'NoBarcode'} - {self.company_name} - {self.part_name}"

    class Meta:
        verbose_name_plural = "Inventories"
        ordering = ["company_name", "part_name"]

    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.selling_price * (1 - self.discount / 100)
        return self.selling_price

    @property
    def actual_quantity(self):
        session_items_total = (
            self.billing_session_items.filter(
                session__user__branch=self.branch
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        actual_available = self.available_quantity - session_items_total

        return max(actual_available, 0)

    def is_quantity_available(self, requested_quantity, exclude_session_item=None):
        """
        Check if requested quantity is available, optionally excluding a specific session item
        """

        actual_available = self.actual_quantity

        # If excluding a specific session item, add its quantity back to available
        if exclude_session_item:
            actual_available += exclude_session_item.quantity

        return actual_available >= requested_quantity


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("initial", "Initial"),
        ("purchase", "Purchase"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
        ("damage", "Damage/Loss"),
    ]

    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="inventory_transactions"
    )

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference_number = models.CharField(
        max_length=50, blank=True, null=True
    )  # For purchase orders, sales orders, etc.
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stock_transactions_user",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()}"

    def save(self, *args, **kwargs):
        # Normalize notes

        self.notes = StringProcessor(self.notes.strip()).title

        # Normalize quantity sign
        if self.transaction_type in ["initial", "purchase"]:
            self.quantity = abs(self.quantity)
        elif self.transaction_type in ["adjustment", "return", "damage"]:
            self.quantity = -abs(self.quantity)

        super().save(*args, **kwargs)

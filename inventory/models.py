from django.db import models
from django.utils import timezone
from django.conf import settings
from suppliers.models import Supplier
from branches.models import Branch
from django import forms


class Inventory(models.Model):
    company_name = models.CharField(max_length=100)
    part_name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Inventories"
        ordering = ["company_name", "part_name"]

    def __str__(self):
        return f"{self.barcode or 'NoBarcode'} - {self.company_name} - {self.part_name}"

    def save(self, *args, **kwargs):
        import random
        import string

        if not self.barcode:
            # Generate a random 6-digit barcode number
            while True:
                barcode = "".join(random.choices(string.digits, k=6))
                if not Inventory.objects.filter(barcode=barcode).exists():
                    self.barcode = barcode
                    break
        super().save(*args, **kwargs)

    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.selling_price * (1 - self.discount / 100)
        return self.selling_price

    @property
    def stock_status(self):
        if self.quantity <= 0:
            return "Out of Stock"
        elif self.quantity <= self.minimum_quantity:
            return "Low Stock"
        return "In Stock"

    def update_stock(
        self, quantity_change, transaction_type, reference_number=None, notes=None
    ):
        """Update stock quantity and create a transaction record"""
        old_quantity = self.quantity
        self.quantity += quantity_change
        self.save()

        # Create transaction record
        StockTransaction.objects.create(
            inventory=self,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            previous_quantity=old_quantity,
            new_quantity=self.quantity,
            reference_number=reference_number,
            notes=notes,
        )


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("purchase", "Purchase"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
        ("damage", "Damage/Loss"),
    ]

    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity_change = (
        models.IntegerField()
    )  # Positive for additions, negative for reductions
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    reference_number = models.CharField(
        max_length=50, blank=True, null=True
    )  # For purchase orders, sales orders, etc.
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.inventory} ({self.quantity_change:+d})"

    @property
    def transaction_date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M")

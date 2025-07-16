from django.db import models
from collections import defaultdict
from decimal import Decimal
from base.stringProcess import StringProcessor


# Create your models here.
class QuoteInventory(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=5)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = StringProcessor(self.name).title
        super().save(*args, **kwargs)


class QuoteMember(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.phone} - {self.address}"

    def save(self, *args, **kwargs):
        self.name = StringProcessor(self.name).title
        self.address = StringProcessor(self.address).title
        super().save(*args, **kwargs)


class QuoteSession(models.Model):
    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    customer = models.ForeignKey(
        QuoteMember,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="customer_quotes",
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default="processing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.customer.name if self.customer else f"Session #{self.pk}"

    @property
    def tax_values_by_gst(self):
        """
        Calculate tax values grouped by GST rate for the quote session.
        """
        gst_groups = defaultdict(
            lambda: {"tax_value": Decimal("0.00"), "total_tax_value": Decimal("0.00")}
        )

        for item in self.quote_items_session.all():
            gst_rate = float(item.quote_inventory.tax)
            gst_groups[gst_rate]["tax_value"] += Decimal(str(item.tax_value))
            gst_groups[gst_rate]["total_tax_value"] += Decimal(str(item.tax_amount))

        return {
            "details": {
                gst: {
                    "tax_value": round(values["tax_value"], 2),
                    "total_tax_value": round(values["total_tax_value"], 2),
                }
                for gst, values in gst_groups.items()
            }
        }

    @property
    def total_tax_value(self):
        """
        Total tax value for the session (sum of all item tax_amounts).
        """
        return sum(item.tax_value for item in self.quote_items_session.all())


class QuoteItem(models.Model):
    quote_session = models.ForeignKey(
        QuoteSession, on_delete=models.CASCADE, related_name="quote_items_session"
    )
    quote_inventory = models.ForeignKey(
        QuoteInventory, on_delete=models.CASCADE, related_name="quote_items_inventory"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"sess {self.quote_session.pk} - {self.quote_inventory.name }"

    @property
    def amount(self):
        return self.quantity * self.price

    @property
    def tax_value(self):
        """
        Taxable value before GST.
        """
        tax_rate = float(self.quote_inventory.tax)
        if tax_rate == 0:
            return self.amount
        return round(float(self.amount) / (1 + tax_rate / 100), 2)

    @property
    def tax_amount(self):
        """
        Calculate GST amount based on the taxable value and GST rate.
        """
        return round(float(self.amount) - float(self.tax_value), 2)

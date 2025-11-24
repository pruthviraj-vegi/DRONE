from django.db import models
from decimal import Decimal
from collections import defaultdict
from branches.models import Branch
from customers.models import Member
from users.models import CustomUser
from inventory.models import Inventory
from base.stringProcess import StringProcessor
from django.db.models import Sum, ExpressionWrapper, F, DecimalField

# Create your models here.


class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        (True, "Cash"),
        (False, "Credit"),
    ]
    PAYMENT_MODE_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("upi", "UPI"),
        ("card", "Card"),
        ("wallet", "Wallet"),
        ("other", "Other"),
    ]

    customer = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="customer_invoices"
    )
    invoice_type = models.BooleanField(default=True, choices=INVOICE_TYPE_CHOICES)
    sale_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sale_user_invoices"
    )
    payment_mode = models.CharField(
        max_length=100, choices=PAYMENT_MODE_CHOICES, default="cash"
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="branch_invoices"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

    @property
    def balance(self):
        return self.total_amount - self.advance_amount

    @property
    def dueAmount(self):
        return self.balance - self.discount_amount

    @property
    def totalQty(self):
        total = self.invoice_items.aggregate(total=Sum("quantity"))["total"]
        return total or Decimal("0.00")

    @property
    def totalAmount(self):
        total = self.invoice_items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                )
            )
        )["total"]
        return total or 0

    @property
    def tax_values_by_gst(self):
        """
        Calculate tax values grouped by GST rate
        """
        gst_groups = defaultdict(
            lambda: {"tax_value": Decimal("0.00"), "total_tax_value": Decimal("0.00")}
        )

        for stock in self.invoice_items.all():
            gst_rate = stock.inventory.gst
            gst_groups[gst_rate]["tax_value"] += Decimal(str(stock.tax_value))
            gst_groups[gst_rate]["total_tax_value"] += Decimal(str(stock.gst_amount))

        return {
            "details": {
                gst: {
                    "tax_value": round(values["tax_value"], 2),
                    "total_tax_value": round(values["total_tax_value"], 2),
                }
                for gst, values in gst_groups.items()
            }
        }

    def save(self, *args, **kwargs):
        self.notes = StringProcessor(self.notes).title
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="invoice_items", on_delete=models.CASCADE
    )
    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="invoice_items_inventory"
    )
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.invoice} - {self.inventory.part_name}"

    @property
    def amount(self):
        return self.price * self.quantity

    @property
    def tax_value(self):
        """
        Taxable value before GST.
        """
        gst_rate = Decimal(self.inventory.gst)
        if gst_rate == 0:
            return self.amount
        return round(self.amount / (1 + gst_rate / 100), 2)

    @property
    def gst_amount(self):
        """
        Calculate GST amount based on the taxable value and GST rate.
        """
        return round(self.amount - self.tax_value, 2)

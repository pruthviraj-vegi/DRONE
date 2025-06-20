from django.db import models

from customers.models import Member
from branches.models import Branch
from users.models import CustomUser
from inventory.models import Inventory

# Create your models here.


class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        (True, "Cash"),
        (False, "Credit"),
    ]
    customer = models.ForeignKey(Member, on_delete=models.CASCADE)
    invoice_type = models.BooleanField(default=True, choices=INVOICE_TYPE_CHOICES)
    sale_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.invoice} - {self.inventory.part_name}"

    @property
    def amount(self):
        return self.price * self.quantity

from django.db import models
from customers.models import Member
from inventory.models import Inventory
from branches.models import Branch
from django.contrib.auth import get_user_model


class BillingSession(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # False when converted to Bill


class BillingSessionItem(models.Model):
    session = models.ForeignKey(
        BillingSession, related_name="items", on_delete=models.CASCADE
    )
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.session.name}"

    @property
    def amount(self):
        return self.quantity * self.price

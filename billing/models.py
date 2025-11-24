from django.db import models
from inventory.models import Inventory, ProductAssembly
from django.contrib.auth import get_user_model
from base.stringProcess import StringProcessor
from django.db.models import F, Sum, ExpressionWrapper, DecimalField


class BillingSession(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # False when converted to Bill

    def __str__(self):
        return self.name

    @property
    def total_amount(self):
        total = self.session_items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                )
            )
        )["total"]
        return total or 0

    def save(self, *args, **kwargs):
        self.name = StringProcessor(self.name).title
        super().save(*args, **kwargs)


class BillingSessionItem(models.Model):
    session = models.ForeignKey(
        BillingSession, related_name="session_items", on_delete=models.CASCADE
    )
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="billing_session_items",
        blank=True,
        null=True,
        help_text="Regular inventory item"
    )
    assembly = models.ForeignKey(
        ProductAssembly,
        on_delete=models.CASCADE,
        related_name="billing_session_items",
        blank=True,
        null=True,
        help_text="If this is an assembly product (Bill of Materials)"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.assembly:
            return f"{self.session.name} - {self.assembly.name}"
        return f"{self.session.name} - {self.inventory.part_name if self.inventory else 'Unknown'}"

    @property
    def amount(self):
        return round(self.quantity * self.price, 2)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure either inventory or assembly is set, but not both
        if not self.inventory and not self.assembly:
            raise ValidationError("Either inventory or assembly must be set.")
        if self.inventory and self.assembly:
            raise ValidationError("Cannot set both inventory and assembly.")

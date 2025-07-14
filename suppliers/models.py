from django.db import models
from django.utils import timezone
from base.stringProcess import StringProcessor


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    tax_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = StringProcessor(self.name).title
        self.address = StringProcessor(self.address).title
        self.tax_number = StringProcessor(self.tax_number).uppercase
        self.notes = StringProcessor(self.notes).title
        super().save(*args, **kwargs)

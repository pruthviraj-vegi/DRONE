from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from branches.models import Branch
from base.stringProcess import StringProcessor


class Member(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="Phone number must be exactly 10 digits.",
            )
        ],
    )
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    branches = models.ManyToManyField(Branch, related_name="members")
    notes = models.TextField(blank=True, help_text="Additional notes about the member")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the member")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Member"
        verbose_name_plural = "Members"

    def __str__(self):
        return self.name

    def get_status_badge_class(self):
        status_classes = {
            "active": "success",
            "inactive": "danger",
            "pending": "warning",
        }
        return status_classes.get(self.status, "secondary")

    def save(self, *args, **kwargs):
        self.name = StringProcessor(self.name).title
        self.address = StringProcessor(self.address).title
        self.notes = StringProcessor(self.notes).title
        super().save(*args, **kwargs)

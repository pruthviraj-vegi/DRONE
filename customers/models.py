from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from branches.models import Branch


class Member(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="members")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the member")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Member"
        verbose_name_plural = "Members"
        unique_together = ["phone", "branch"]

    def __str__(self):
        return self.name

    def get_status_badge_class(self):
        status_classes = {
            "active": "success",
            "inactive": "danger",
            "pending": "warning",
        }
        return status_classes.get(self.status, "secondary")

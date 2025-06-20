from django.db import models
from django.utils import timezone


class Branch(models.Model):
    BRANCH_TYPE_CHOICES = (
        ("main", "Main Branch"),
        ("sub", "Sub Branch"),
    )

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=10, choices=BRANCH_TYPE_CHOICES)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sub_branches",
    )
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ["name"]

    def __str__(self):
        return self.name

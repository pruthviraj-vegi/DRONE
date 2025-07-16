from django.db import models
from customers.models import Member
from django.utils import timezone
from users.models import CustomUser


# Create your models here.
class Credit(models.Model):

    CHOICES = [
        (True, "Paid"),
        (False, "Purchased"),
    ]

    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, null=True, related_name="credits"
    )
    paid = models.BooleanField(default=True, choices=CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, help_text="Additional notes about the credit")
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="credits_created_by"
    )
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.member)

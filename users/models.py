# users/models.py
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from base.stringProcess import StringProcessor

from branches.models import Branch


ROLE_CHOICES = (
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("staff", "Staff"),
)


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Users must have a phone number")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="branch_users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name", "role"]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    def save(self, *args, **kwargs):
        self.full_name = StringProcessor(self.full_name).title
        self.email = StringProcessor(self.email).capitalized
        super().save(*args, **kwargs)

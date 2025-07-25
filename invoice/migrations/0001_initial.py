# Generated by Django 5.2.1 on 2025-07-05 12:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("customers", "0001_initial"),
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "invoice_type",
                    models.BooleanField(
                        choices=[(True, "Cash"), (False, "Credit")], default=True
                    ),
                ),
                (
                    "payment_mode",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("bank", "Bank"),
                            ("upi", "UPI"),
                            ("card", "Card"),
                            ("wallet", "Wallet"),
                            ("other", "Other"),
                        ],
                        default="cash",
                        max_length=100,
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(decimal_places=2, max_digits=12, default=0),
                ),
                (
                    "advance_amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_invoices",
                        to="customers.member",
                    ),
                ),
                (
                    "sale_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sale_user_invoices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="branch_invoices",
                        to="branches.branch",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InvoiceItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "purchased_price",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "quantity",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "inventory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoice_items_inventory",
                        to="inventory.inventory",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoice_items",
                        to="invoice.invoice",
                    ),
                ),
            ],
        ),
    ]

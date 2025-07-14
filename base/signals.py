from django.db.models.signals import post_save, post_delete
from django.db.models import Sum, Q, Value
import logging
from invoice.models import InvoiceItem
from django.dispatch import receiver
from inventory.models import StockTransaction, Inventory
from inventoryManage.models import BranchInventory


logger = logging.getLogger(__name__)


def set_quantity(inventory):
    try:

        transaction_quantity = (
            inventory.inventory_transactions.all().aggregate(total=Sum("quantity"))[
                "total"
            ]
            or 0
        )

        transfer_quantity = (
            inventory.branch_inventory_inventory.all().aggregate(total=Sum("quantity"))[
                "total"
            ]
            or 0
        )

        sold_quantity = (
            inventory.invoice_items_inventory.filter(
                invoice__branch=inventory.branch
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        available_quantity = transaction_quantity - transfer_quantity - sold_quantity

        if inventory.available_quantity != available_quantity:
            inventory.available_quantity = available_quantity
            inventory.save()

        return inventory.available_quantity
    except Exception as e:
        logger.error(f"Error in set_quantity: {e}")
        return 0


def set_qty_branch(branch_inventory):
    try:
        transaction_quantity = (
            branch_inventory.transactions.all().aggregate(total=Sum("quantity"))[
                "total"
            ]
            or 0
        )
        sold_quantity = (
            branch_inventory.inventory.invoice_items_inventory.filter(
                invoice__branch=branch_inventory.branch
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        print(transaction_quantity, sold_quantity)
        available_quantity = transaction_quantity - sold_quantity

        if branch_inventory.available_quantity != available_quantity:
            branch_inventory.available_quantity = available_quantity
            branch_inventory.save()

        return branch_inventory.available_quantity

    except Exception as e:
        logger.error(f"Error in set_qty_branch: {e}")
        return 0


def staff_quantity_update(invoice_item):
    branch = invoice_item.invoice.branch

    branch_inventory = BranchInventory.objects.get(
        branch=branch, inventory=invoice_item.inventory
    )

    try:
        sold_quantity = (
            invoice_item.inventory.invoice_items_inventory.filter(
                invoice__branch=invoice_item.invoice.branch
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        transfer_quantity = (
            invoice_item.inventory.branch_inventory_inventory.all().aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        branch_inventory.available_quantity = transfer_quantity - sold_quantity
        branch_inventory.save()

    except Exception as e:
        logger.error(f"Error in staff_quantity_update: {e}")
        return 0


@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def quantity_update_by_invoice(sender, instance, **kwargs):

    if instance.invoice.sale_user.role == "admin":
        inventory = instance.inventory
        set_quantity(inventory)
    else:
        staff_quantity_update(instance)


@receiver(post_save, sender=StockTransaction)
@receiver(post_delete, sender=StockTransaction)
def quantity_update_by_transation(sender, instance, **kwargs):
    inventory = instance.inventory
    set_quantity(inventory)


@receiver(post_save, sender=BranchInventory)
@receiver(post_delete, sender=BranchInventory)
def quantity_update_by_branchInventory(sender, instance, **kwargs):
    inventory = instance.inventory
    set_quantity(inventory)
    set_qty_branch(instance)

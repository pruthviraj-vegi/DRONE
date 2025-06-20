from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BranchInventoryTransferForm, BranchInventoryTransferItemForm
from .models import BranchInventory, BranchInventoryTransaction, TransactionDetail
from django.forms import formset_factory
from django.core.paginator import Paginator
from Drone.decorators import admin_required
from django.db import transaction


@admin_required
def branch_inventory_transfer_list(request):
    transactions = TransactionDetail.objects.select_related(
        "from_branch", "to_branch"
    ).order_by("-created_at")
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "inventoryManage/main_page.html",
        {"page_obj": page_obj},
    )


@admin_required
def branch_inventory_transfer(request):
    TransferItemFormSet = formset_factory(BranchInventoryTransferItemForm, extra=1)
    if request.method == "POST":
        form = BranchInventoryTransferForm(
            request.POST, user_branch=request.user.branch
        )
        formset = TransferItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            to_branch = form.cleaned_data["to_branch"]
            notes = form.cleaned_data.get("notes", "")

            with transaction.atomic():
                transaction_detail = TransactionDetail(
                    from_branch=request.user.branch,
                    to_branch=to_branch,
                    transfered_by=request.user,
                )
                transaction_detail.save()

                for item_form in formset:
                    if not item_form.cleaned_data:
                        continue
                    inventory = item_form.cleaned_data["inventory"]
                    quantity = item_form.cleaned_data["quantity"]

                    # get if existed inventory
                    branch_inv = BranchInventory.objects.filter(
                        inventory=inventory, branch=to_branch
                    ).first()

                    if branch_inv:
                        old_qty = branch_inv.quantity
                        branch_inv.quantity += quantity
                        branch_inv.save()
                        transaction_type = "update"
                    else:
                        branch_inv = BranchInventory.objects.create(
                            inventory=inventory, branch=to_branch, quantity=quantity
                        )
                        old_qty = 0
                        transaction_type = "forward"

                    # Log transaction
                    BranchInventoryTransaction.objects.create(
                        branch_inventory=branch_inv,
                        transaction_detail=transaction_detail,
                        transaction_type=transaction_type,
                        quantity_change=quantity,
                        previous_quantity=old_qty,
                        new_quantity=branch_inv.quantity,
                        notes=notes,
                    )
                messages.success(request, "Inventory transferred successfully.")
                return redirect("inventoryManage:branch_inventory_transfer")
    else:
        form = BranchInventoryTransferForm(user_branch=request.user.branch)
        formset = TransferItemFormSet()

    return render(
        request,
        "inventoryManage/form.html",
        {"form": form, "formset": formset},
    )


@admin_required
def transaction_details(request, transaction_id):
    transaction = BranchInventoryTransaction.objects.select_related(
        "branch_inventory__inventory", "branch_inventory__branch"
    ).filter(transaction_detail_id=transaction_id)
    paginator = Paginator(transaction, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "inventoryManage/details_page.html",
        {"page_obj": page_obj},
    )

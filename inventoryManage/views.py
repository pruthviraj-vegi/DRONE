from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BranchInventoryTransferForm, BranchInventoryTransferItemForm
from .models import BranchInventory, BranchInventoryTransaction, TransactionDetail
from django.forms import formset_factory
from django.core.paginator import Paginator
from Drone.decorators import admin_required
from django.db import transaction
from base.utility import get_basic_data
from django.db.models import Q


@admin_required
def branch_inventory_transfer_list(request):
    template_name = "inventoryManage/main_page.html"
    return render(request, template_name)


@admin_required
def fetch_transactions(request):
    basic_data = get_basic_data(request)
    query = Q()
    search_query = basic_data["search_query"]
    if search_query:
        query &= Q(name__icontains=search_query)

    transactions = TransactionDetail.objects.filter(query).order_by(
        basic_data["sort_column"]
    )
    transactions = transactions[
        basic_data["start"] : basic_data["start"] + basic_data["limit"]
    ]

    return render(request, "inventoryManage/fetch.html", {"data": transactions})


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
                        branch_inv.quantity += quantity
                        branch_inv.save()
                        transaction_type = "update"
                    else:
                        branch_inv = BranchInventory.objects.create(
                            inventory=inventory, branch=to_branch, quantity=quantity
                        )
                        transaction_type = "forward"

                    # Log transaction
                    BranchInventoryTransaction.objects.create(
                        branch_inventory=branch_inv,
                        transaction_detail=transaction_detail,
                        transaction_type=transaction_type,
                        quantity=quantity,
                        notes=notes,
                    )
                    branch_inv.save()
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
    transaction = (
        BranchInventoryTransaction.objects.select_related(
            "branch_inventory__inventory", "branch_inventory__branch"
        )
        .filter(transaction_detail_id=transaction_id)
        .order_by("-id")
    )
    paginator = Paginator(transaction, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "inventoryManage/details_page.html",
        {"page_obj": page_obj},
    )

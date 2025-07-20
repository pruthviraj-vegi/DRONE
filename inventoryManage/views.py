from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BranchInventoryTransferForm, create_transfer_item_formset
from .models import BranchInventory, BranchInventoryTransaction, TransactionDetail
from inventory.models import Inventory
from django.forms import formset_factory
from django.core.paginator import Paginator
from Drone.decorators import admin_required
from django.db import transaction
from base.utility import get_basic_data
from django.db.models import Q
from django.http import JsonResponse


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
def fetch_inventory_data(request):
    """API endpoint to fetch inventory data for the current user's branch"""
    try:
        user_branch = request.user.branch
        if not user_branch:
            return JsonResponse({"error": "No branch assigned to user"}, status=400)

        inventory_data = []

        # First try to get data from BranchInventory
        branch_inventories = BranchInventory.objects.filter(
            branch=user_branch
        ).select_related("inventory")

        if branch_inventories.exists():
            # Use BranchInventory data
            for branch_inv in branch_inventories:
                inventory_data.append(
                    {
                        "id": branch_inv.inventory.id,
                        "company_name": branch_inv.inventory.company_name,
                        "part_name": branch_inv.inventory.part_name,
                        "barcode": branch_inv.inventory.barcode,
                        "actual_quantity": float(branch_inv.actual_quantity()),
                        "minimum_quantity": float(
                            branch_inv.inventory.minimum_quantity
                        ),
                        "uom": branch_inv.inventory.uom,
                    }
                )
        else:
            # Fallback to direct inventory data from user's branch
            inventories = Inventory.objects.filter(branch=user_branch, is_active=True)
            for inventory in inventories:
                inventory_data.append(
                    {
                        "id": inventory.id,
                        "company_name": inventory.company_name,
                        "part_name": inventory.part_name,
                        "barcode": inventory.barcode,
                        "actual_quantity": float(inventory.available_quantity),
                        "minimum_quantity": float(inventory.minimum_quantity),
                        "uom": inventory.uom,
                    }
                )

        return JsonResponse(inventory_data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@admin_required
def branch_inventory_transfer(request):
    # Create formset with user's branch
    TransferItemFormSet = create_transfer_item_formset(request.user.branch)

    if request.method == "POST":
        form = BranchInventoryTransferForm(
            request.POST, user_branch=request.user.branch
        )
        formset = TransferItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            to_branch = form.cleaned_data["to_branch"]
            notes = form.cleaned_data.get("notes", "")

            # Validate quantities before processing
            validation_errors = []
            for i, item_form in enumerate(formset):
                if not item_form.cleaned_data:
                    continue
                inventory = item_form.cleaned_data["inventory"]
                quantity = item_form.cleaned_data["quantity"]

                # Check if item exists in user's branch
                try:
                    # First try to get BranchInventory record
                    branch_inventory = BranchInventory.objects.get(
                        inventory=inventory, branch=request.user.branch
                    )
                    actual_available = branch_inventory.actual_quantity()
                except BranchInventory.DoesNotExist:
                    # If no BranchInventory record, check direct inventory
                    if inventory.branch == request.user.branch:
                        actual_available = float(inventory.available_quantity)
                    else:
                        validation_errors.append(
                            f"Row {i+1}: Item {inventory.part_name} is not available in your branch"
                        )
                        continue

                if quantity > actual_available:
                    validation_errors.append(
                        f"Row {i+1}: Quantity ({quantity}) cannot exceed available stock ({actual_available}) for {inventory.part_name}"
                    )

            if validation_errors:
                for error in validation_errors:
                    messages.error(request, error)
                return render(
                    request,
                    "inventoryManage/form.html",
                    {"form": form, "formset": formset},
                )

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

                    # Handle source branch inventory reduction
                    try:
                        # Try to get BranchInventory record for source branch
                        source_branch_inv = BranchInventory.objects.get(
                            inventory=inventory, branch=request.user.branch
                        )
                        source_branch_inv.quantity -= quantity
                        source_branch_inv.save()
                    except BranchInventory.DoesNotExist:
                        # If no BranchInventory record, reduce from direct inventory
                        if inventory.branch == request.user.branch:
                            inventory.available_quantity -= quantity
                            inventory.save()
                        else:
                            messages.error(
                                request,
                                f"Item {inventory.part_name} is not available in your branch",
                            )
                            continue

                    # Handle destination branch inventory
                    dest_branch_inv = BranchInventory.objects.filter(
                        inventory=inventory, branch=to_branch
                    ).first()

                    if dest_branch_inv:
                        dest_branch_inv.quantity += quantity
                        dest_branch_inv.save()
                        transaction_type = "update"
                    else:
                        dest_branch_inv = BranchInventory.objects.create(
                            inventory=inventory, branch=to_branch, quantity=quantity
                        )
                        transaction_type = "forward"

                    # Log transaction
                    BranchInventoryTransaction.objects.create(
                        branch_inventory=dest_branch_inv,
                        transaction_detail=transaction_detail,
                        transaction_type=transaction_type,
                        quantity=quantity,
                        notes=notes,
                    )
                    dest_branch_inv.save()
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


@admin_required
def debug_inventory(request):
    """Debug view to check what inventory items are available"""
    user_branch = request.user.branch

    # Check BranchInventory records
    branch_inventories = BranchInventory.objects.filter(branch=user_branch)

    # Check direct Inventory records
    direct_inventories = Inventory.objects.filter(branch=user_branch, is_active=True)

    context = {
        "user_branch": user_branch,
        "branch_inventories": branch_inventories,
        "direct_inventories": direct_inventories,
        "branch_inventory_count": branch_inventories.count(),
        "direct_inventory_count": direct_inventories.count(),
    }

    return render(request, "inventoryManage/debug.html", context)

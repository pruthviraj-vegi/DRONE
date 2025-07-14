from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import Inventory, StockTransaction
from Drone.decorators import admin_required
from inventoryManage.models import BranchInventory
from .forms import StockTransactionForm, InventoryCreateForm
from base.utility import get_basic_data
from django.db import transaction


@admin_required
def inventory_list(request):

    template_name = "inventory/main_page.html"

    return render(request, template_name)


def fetch_inventory(request):
    basic_data = get_basic_data(request)

    # Build Q object for search
    search_query = basic_data["search_query"]
    q_obj = Q()
    if search_query:
        q_obj |= Q(company_name__icontains=search_query)
        q_obj |= Q(part_name__icontains=search_query)
        q_obj |= Q(part_number__icontains=search_query)

    # Filter by stock status (if needed, update logic for new structure)
    stock_status = request.GET.get("stock_status", "")
    if stock_status == "out":
        q_obj &= Q(branchinventory__quantity=0)
    elif stock_status == "low":
        q_obj &= Q(branchinventory__quantity__lte=F("minimum_quantity"))

    queryset = Inventory.objects.filter(q_obj).order_by(basic_data["sort_column"])
    queryset = queryset[basic_data["start"] : basic_data["start"] + basic_data["limit"]]

    context = {
        "data": queryset,
    }
    return render(request, "inventory/fetch.html", context)


@admin_required
def inventory_create(request):
    if request.method == "POST":
        inventory_form = InventoryCreateForm(request.POST)
        with transaction.atomic():
            if inventory_form.is_valid():
                inventory = inventory_form.save(commit=False)
                inventory.created_by = request.user
                inventory.available_quantity = inventory.quantity
                inventory.branch = request.user.branch
                inventory.save()
                # Create initial stock transaction for main branch
                if inventory.quantity > 0:
                    StockTransaction.objects.create(
                        inventory=inventory,
                        transaction_type="initial",
                        quantity=inventory.quantity,
                        created_by=request.user,
                        notes="Initial stock on creation",
                    )
                messages.success(
                    request,
                    f'Inventory item "{inventory.part_name}" has been created successfully.',
                )
                return redirect("inventory:inventory_list")
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        inventory_form = InventoryCreateForm()
    context = {
        "title": "Create New Inventory Item",
        "form": inventory_form,
    }
    return render(request, "inventory/inventory_form.html", context)


@admin_required
def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        form = InventoryCreateForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Inventory item "{form.cleaned_data["part_name"]}" has been updated successfully.',
            )
            return redirect("inventory:inventory_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InventoryCreateForm(instance=inventory)
    context = {
        "form": form,
        "title": f"Edit Inventory Item: {inventory}",
    }
    return render(request, "inventory/inventory_form.html", context)


@admin_required
def inventory_delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == "POST":
        inventory_name = str(inventory)
        inventory.delete()
        messages.success(
            request, f'Inventory item "{inventory_name}" has been deleted successfully.'
        )
        return redirect("inventory:inventory_list")

    return render(
        request, "inventory/inventory_confirm_delete.html", {"inventory": inventory}
    )


@admin_required
def stock_transaction_list(request, inventory_id):
    inventory = get_object_or_404(Inventory, pk=inventory_id)

    transaction_type = request.GET.get("type", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    q_obj = Q()
    if transaction_type:
        q_obj &= Q(transaction_type=transaction_type)
    if start_date:
        q_obj &= Q(created_at__gte=start_date)
    if end_date:
        q_obj &= Q(created_at__lte=end_date)

    transactions = inventory.inventory_transactions.filter(q_obj)

    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "inventory": inventory,
        "page_obj": page_obj,
        "transaction_type": transaction_type,
        "start_date": start_date,
        "end_date": end_date,
        "transaction_types": dict(StockTransaction.TRANSACTION_TYPES),
    }
    return render(request, "inventory/stock_transaction_list.html", context)


@admin_required
def update_stock(request, inventory_id):
    inventory = get_object_or_404(Inventory, pk=inventory_id)

    if request.method == "POST":
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.inventory = inventory
            transaction.branch = request.user.branch
            transaction.created_by = request.user
            transaction.save()
            # Update inventory quantity
            messages.success(
                request,
                f"Stock updated successfully. New quantity: {transaction.quantity}",
            )
            return redirect(
                "inventory:stock_transaction_list", inventory_id=inventory.id
            )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StockTransactionForm()

    context = {
        "inventory": inventory,
        "form": form,
    }
    return render(request, "inventory/update_stock.html", context)


def branch_inventory_list(request):
    branch = getattr(request.user, "branch", None)
    if not branch:
        return render(
            request,
            "inventory/branch_inventory_list.html",
            {"error": "No branch assigned to your user."},
        )
    branch_inventory_qs = BranchInventory.objects.select_related("inventory").filter(
        branch=branch
    )
    paginator = Paginator(branch_inventory_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "inventory/branch_inventory_list.html", {"page_obj": page_obj}
    )

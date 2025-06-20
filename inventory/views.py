from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import Inventory, StockTransaction
from suppliers.models import Supplier
from Drone.decorators import admin_required
from inventoryManage.models import BranchInventory
from .forms import InventoryForm, StockTransactionForm


@admin_required
def inventory_list(request):
    inventory_items = Inventory.objects.all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        inventory_items = inventory_items.filter(
            Q(company_name__icontains=search_query)
            | Q(part_name__icontains=search_query)
            | Q(part_number__icontains=search_query)
        )

    # Filter by supplier
    supplier_filter = request.GET.get("supplier", "")
    if supplier_filter:
        inventory_items = inventory_items.filter(supplier_id=supplier_filter)

    # Filter by stock status
    stock_status = request.GET.get("stock_status", "")
    if stock_status:
        if stock_status == "out":
            inventory_items = inventory_items.filter(quantity=0)
        elif stock_status == "low":
            inventory_items = inventory_items.filter(
                quantity__lte=F("minimum_quantity")
            )

    # Pagination
    paginator = Paginator(inventory_items, 10)  # Show 10 items per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "supplier_filter": supplier_filter,
        "stock_status": stock_status,
        "suppliers": Supplier.objects.filter(is_active=True),
    }
    return render(request, "inventory/inventory_list.html", context)


@admin_required
def inventory_create(request):
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Inventory item "{form.cleaned_data["part_name"]}" has been created successfully.',
            )
            return redirect("inventory:inventory_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InventoryForm()
    context = {
        "title": "Create New Inventory Item",
        "form": form,
    }
    return render(request, "inventory/inventory_form.html", context)


@admin_required
def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=inventory)
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
        form = InventoryForm(instance=inventory)
    context = {
        "inventory": inventory,
        "title": f"Edit Inventory Item: {inventory}",
        "form": form,
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
    transactions = inventory.transactions.all()

    # Filter by transaction type
    transaction_type = request.GET.get("type", "")
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Filter by date range
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__lte=end_date)

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
            transaction.previous_quantity = inventory.quantity
            transaction.new_quantity = inventory.quantity + transaction.quantity_change
            transaction.created_by = request.user
            transaction.save()
            # Update inventory quantity
            inventory.quantity = transaction.new_quantity
            inventory.save()
            messages.success(
                request,
                f"Stock updated successfully. New quantity: {inventory.quantity}",
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from .models import Inventory, StockTransaction
from suppliers.models import Supplier
from Drone.decorators import admin_required


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
        company_name = request.POST.get("company_name")
        part_name = request.POST.get("part_name")
        part_number = request.POST.get("part_number")
        description = request.POST.get("description")
        purchased_price = request.POST.get("purchased_price")
        selling_price = request.POST.get("selling_price")
        discount = request.POST.get("discount", 0)
        supplier_id = request.POST.get("supplier")
        quantity = request.POST.get("quantity", 0)
        minimum_quantity = request.POST.get("minimum_quantity", 0)
        location = request.POST.get("location")

        if company_name and part_name and purchased_price and selling_price:
            try:
                supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None
                inventory = Inventory.objects.create(
                    company_name=company_name,
                    part_name=part_name,
                    part_number=part_number,
                    description=description,
                    purchased_price=purchased_price,
                    selling_price=selling_price,
                    discount=discount,
                    supplier=supplier,
                    quantity=quantity,
                    minimum_quantity=minimum_quantity,
                    location=location,
                )
                messages.success(
                    request,
                    f'Inventory item "{inventory}" has been created successfully.',
                )
                return redirect("inventory:inventory_list")
            except Exception as e:
                messages.error(request, f"Error creating inventory item: {str(e)}")
        else:
            messages.error(request, "Please fill in all required fields.")

    context = {
        "title": "Create New Inventory Item",
        "suppliers": Supplier.objects.filter(is_active=True),
    }
    return render(request, "inventory/inventory_form.html", context)


@admin_required
def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == "POST":
        company_name = request.POST.get("company_name")
        part_name = request.POST.get("part_name")
        part_number = request.POST.get("part_number")
        description = request.POST.get("description")
        purchased_price = request.POST.get("purchased_price")
        selling_price = request.POST.get("selling_price")
        discount = request.POST.get("discount", 0)
        supplier_id = request.POST.get("supplier")
        quantity = request.POST.get("quantity", 0)
        minimum_quantity = request.POST.get("minimum_quantity", 0)
        location = request.POST.get("location")
        is_active = request.POST.get("is_active") == "on"

        if company_name and part_name and purchased_price and selling_price:
            try:
                supplier = Supplier.objects.get(id=supplier_id) if supplier_id else None
                inventory.company_name = company_name
                inventory.part_name = part_name
                inventory.part_number = part_number
                inventory.description = description
                inventory.purchased_price = purchased_price
                inventory.selling_price = selling_price
                inventory.discount = discount
                inventory.supplier = supplier
                inventory.quantity = quantity
                inventory.minimum_quantity = minimum_quantity
                inventory.location = location
                inventory.is_active = is_active
                inventory.save()

                messages.success(
                    request,
                    f'Inventory item "{inventory}" has been updated successfully.',
                )
                return redirect("inventory:inventory_list")
            except Exception as e:
                messages.error(request, f"Error updating inventory item: {str(e)}")
        else:
            messages.error(request, "Please fill in all required fields.")

    context = {
        "inventory": inventory,
        "title": f"Edit Inventory Item: {inventory}",
        "suppliers": Supplier.objects.filter(is_active=True),
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
        transaction_type = request.POST.get("transaction_type")
        quantity_change = int(request.POST.get("quantity_change", 0))
        reference_number = request.POST.get("reference_number")
        notes = request.POST.get("notes")

        if transaction_type and quantity_change != 0:
            try:
                # Create transaction record
                transaction = StockTransaction.objects.create(
                    inventory=inventory,
                    transaction_type=transaction_type,
                    quantity_change=quantity_change,
                    previous_quantity=inventory.quantity,
                    new_quantity=inventory.quantity + quantity_change,
                    reference_number=reference_number,
                    notes=notes,
                    created_by=request.user,
                )

                # Update inventory quantity
                inventory.quantity += quantity_change
                inventory.save()

                messages.success(
                    request,
                    f"Stock updated successfully. New quantity: {inventory.quantity}",
                )
                return redirect(
                    "inventory:stock_transaction_list", inventory_id=inventory.id
                )
            except Exception as e:
                messages.error(request, f"Error updating stock: {str(e)}")
        else:
            messages.error(
                request, "Please provide valid transaction type and quantity change."
            )

    context = {
        "inventory": inventory,
        "transaction_types": dict(StockTransaction.TRANSACTION_TYPES),
    }
    return render(request, "inventory/update_stock.html", context)

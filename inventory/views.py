from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F, Count, Sum
from django.http import JsonResponse
from .models import Inventory, StockTransaction
from Drone.decorators import admin_required
from inventoryManage.models import BranchInventory
from .forms import StockTransactionForm, InventoryCreateForm
from base.utility import get_basic_data
from django.db import transaction
import csv
import io
from django.http import HttpResponse
from branches.models import Branch


@admin_required
def quick_search(request):
    """Quick search by barcode or part name"""
    search_term = request.GET.get("q", "").strip()

    if not search_term:
        return JsonResponse({"error": "Search term is required"}, status=400)

    # Search by barcode first (exact match)
    inventory = Inventory.objects.filter(
        barcode=search_term, branch=request.user.branch
    ).first()

    if inventory:
        return JsonResponse(
            {
                "found": True,
                "inventory": {
                    "id": inventory.id,
                    "barcode": inventory.barcode,
                    "company_name": inventory.company_name,
                    "part_name": inventory.part_name,
                    "part_number": inventory.part_number,
                    "actual_quantity": float(inventory.actual_quantity),
                    "uom": inventory.uom,
                    "selling_price": float(inventory.selling_price),
                    "discount": float(inventory.discount),
                    "discounted_price": float(inventory.discounted_price),
                    "is_active": inventory.is_active,
                    "stock_status": inventory.stock_status_badge,
                },
            }
        )

    # If not found by barcode, search by part name (partial match)
    inventories = Inventory.objects.filter(
        Q(part_name__icontains=search_term) | Q(company_name__icontains=search_term),
        branch=request.user.branch,
    )[
        :5
    ]  # Limit to 5 results

    if inventories:
        results = []
        for inv in inventories:
            results.append(
                {
                    "id": inv.id,
                    "barcode": inv.barcode,
                    "company_name": inv.company_name,
                    "part_name": inv.part_name,
                    "part_number": inv.part_number,
                    "actual_quantity": float(inv.actual_quantity),
                    "uom": inv.uom,
                    "selling_price": float(inv.selling_price),
                    "discount": float(inv.discount),
                    "discounted_price": float(inv.discounted_price),
                    "is_active": inv.is_active,
                    "stock_status": inv.stock_status_badge,
                }
            )

        return JsonResponse({"found": True, "multiple": True, "inventories": results})

    return JsonResponse(
        {"found": False, "message": f'No inventory found for "{search_term}"'}
    )


@admin_required
def bulk_import(request):
    """Bulk import inventory items from CSV"""
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "Please select a CSV file.")
            return redirect("inventory:bulk_import")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect("inventory:bulk_import")

        try:
            # Read CSV file
            decoded_file = csv_file.read().decode("utf-8")
            csv_data = csv.DictReader(io.StringIO(decoded_file))

            success_count = 0
            error_count = 0
            errors = []

            with transaction.atomic():
                for row in csv_data:
                    try:
                        # Create inventory item
                        inventory = Inventory(
                            company_name=row.get("company_name", "").strip(),
                            part_name=row.get("part_name", "").strip(),
                            part_number=row.get("part_number", "").strip(),
                            uom=row.get("uom", "PCS"),
                            quantity=float(row.get("quantity", 0)),
                            purchased_price=float(row.get("purchased_price", 0)),
                            selling_price=float(row.get("selling_price", 0)),
                            discount=float(row.get("discount", 0)),
                            minimum_quantity=float(row.get("minimum_quantity", 0)),
                            gst=float(row.get("gst", 5)),
                            is_active=row.get("is_active", "True").lower() == "true",
                            notes=row.get("notes", "").strip(),
                            created_by=request.user,
                            branch=request.user.branch,
                        )
                        inventory.save()

                        # Create initial stock transaction if quantity > 0
                        if inventory.quantity > 0:
                            StockTransaction.objects.create(
                                inventory=inventory,
                                transaction_type="initial",
                                quantity=inventory.quantity,
                                created_by=request.user,
                                notes="Initial stock from bulk import",
                            )

                        success_count += 1

                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {success_count + error_count}: {str(e)}")

            if success_count > 0:
                messages.success(
                    request, f"Successfully imported {success_count} inventory items."
                )

            if error_count > 0:
                messages.warning(
                    request,
                    f"Failed to import {error_count} items. Check the errors below.",
                )
                for error in errors[:5]:  # Show first 5 errors
                    messages.error(request, error)

            return redirect("inventory:inventory_list")

        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
            return redirect("inventory:bulk_import")

    return render(request, "inventory/bulk_import.html")


@admin_required
def download_csv_template(request):
    """Download CSV template for bulk import"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="inventory_template.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "company_name",
            "part_name",
            "part_number",
            "uom",
            "quantity",
            "purchased_price",
            "selling_price",
            "discount",
            "minimum_quantity",
            "gst",
            "is_active",
            "notes",
        ]
    )
    writer.writerow(
        [
            "Toyota",
            "Oil Filter",
            "TOY-001",
            "PCS",
            "10",
            "50.00",
            "75.00",
            "5.00",
            "2",
            "5.00",
            "True",
            "High quality oil filter",
        ]
    )

    return response


@admin_required
def inventory_dashboard(request):
    """Dashboard view showing inventory statistics"""
    branch = request.user.branch

    # Get inventory statistics
    total_items = Inventory.objects.filter(branch=branch).count()
    active_items = Inventory.objects.filter(branch=branch, is_active=True).count()
    out_of_stock = Inventory.objects.filter(branch=branch, available_quantity=0).count()
    low_stock = Inventory.objects.filter(
        branch=branch,
        available_quantity__lte=F("minimum_quantity"),
        available_quantity__gt=0,
    ).count()

    # Get recent transactions
    recent_transactions = (
        StockTransaction.objects.filter(inventory__branch=branch)
        .select_related("inventory", "created_by")
        .order_by("-created_at")[:10]
    )

    # Get low stock items
    low_stock_items = Inventory.objects.filter(
        branch=branch,
        available_quantity__lte=F("minimum_quantity"),
        available_quantity__gt=0,
    ).order_by("available_quantity")[:5]

    # Get out of stock items
    out_of_stock_items = Inventory.objects.filter(
        branch=branch, available_quantity=0
    ).order_by("part_name")[:5]

    context = {
        "total_items": total_items,
        "active_items": active_items,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "recent_transactions": recent_transactions,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
    }

    return render(request, "inventory/dashboard.html", context)


@admin_required
def inventory_list(request):

    branch_list = Branch.objects.filter(type="sub").values_list("name", flat=True)

    template_name = "inventory/main_page.html"

    return render(request, template_name, {"branchs": branch_list})


def fetch_inventory(request):
    basic_data = get_basic_data(request)

    # Build Q object for search
    search_query = basic_data["search_query"]
    q_obj = Q()
    if search_query:
        q_obj |= Q(company_name__icontains=search_query)
        q_obj |= Q(part_name__icontains=search_query)
        q_obj |= Q(part_number__icontains=search_query)

    branch_name = request.GET.get("branch_name", "")

    if branch_name:

        branch_inventory = BranchInventory.objects.select_related("inventory").filter(
            branch=Branch.objects.get(name=branch_name)
        )
        return render(
            request,
            "inventory/branch_inventory_fetch.html",
            {"inventory": branch_inventory},
        )

    # Filter by stock status
    stock_status = request.GET.get("stock_status", "")
    if stock_status == "out":
        # Items with zero or negative actual quantity
        q_obj &= Q(available_quantity=0)
    elif stock_status == "low":
        # Items where available quantity is less than or equal to minimum quantity
        q_obj &= Q(available_quantity__lte=F("minimum_quantity"))

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
        save_and_add = request.POST.get("save_and_add") == "true"

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

                if save_and_add:
                    messages.success(
                        request,
                        f'Inventory item "{inventory.part_name}" has been created successfully. You can now add another item.',
                    )
                    # Redirect back to the create form with a fresh form
                    return redirect("inventory:inventory_create")
                else:
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
        save_and_add = request.POST.get("save_and_add") == "true"
        print_barcode_after_save = request.POST.get("print_barcode") == "true"

        if form.is_valid():
            form.save()

            if print_barcode_after_save:
                messages.success(
                    request,
                    f'Inventory item "{form.cleaned_data["part_name"]}" has been updated successfully. Generating barcode...',
                )
                # Redirect to existing barcode creation function in report app
                return redirect("report:createBarcode", pk=inventory.pk)
            elif save_and_add:
                messages.success(
                    request,
                    f'Inventory item "{form.cleaned_data["part_name"]}" has been updated successfully. You can now add another item.',
                )
                # Redirect to create form for adding another item
                return redirect("inventory:inventory_create")
            else:
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

    return render(
        request,
        "inventory/branch_inventory_list.html",
    )


def branch_inventory_fetch(request, branch_name=None):

    if branch_name:
        branch = Branch.objects.get(name=branch_name)
    else:
        branch = getattr(request.user, "branch", None)

    branch_inventory = BranchInventory.objects.select_related("inventory").filter(
        branch=branch
    )
    return render(
        request,
        "inventory/branch_inventory_fetch.html",
        {"inventory": branch_inventory},
    )

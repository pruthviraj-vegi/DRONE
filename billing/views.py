from django.shortcuts import render, redirect, get_object_or_404
from .models import BillingSession, BillingSessionItem
from inventory.models import Inventory, ProductAssembly
from inventoryManage.models import BranchInventory
from django.contrib import messages
from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Q
from decimal import Decimal

# Create your views here.


def billing_session_list(request):
    sessions = BillingSession.objects.filter(user=request.user, is_active=True)
    return render(request, "billing/session_list.html", {"sessions": sessions})


def billing_session_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            session = BillingSession.objects.create(user=request.user, name=name)
            return redirect("billing:session_detail", session_id=session.id)
        messages.error(request, "Session name is required.")
    return render(request, "billing/session_create.html")


def billing_session_detail(request, session_id):
    session = get_object_or_404(
        BillingSession, id=session_id, user=request.user, is_active=True
    )
    items = session.session_items.select_related("inventory").all()
    return render(
        request, "billing/session_detail.html", {"session": session, "items": items}
    )


def add_item_by_barcode(request, session_id):
    session = get_object_or_404(
        BillingSession, id=session_id, user=request.user, is_active=True
    )

    if request.method == "POST":
        barcode = request.POST.get("barcode")
        quantity = Decimal(
            request.POST.get("quantity", 1)
        )  # Get quantity from POST or default to 1

        try:
            # First, check if barcode belongs to an assembly (assemblies are shared across branches)
            assembly = ProductAssembly.objects.filter(
                barcode=barcode, is_active=True
            ).first()

            if assembly:
                # Handle assembly barcode (assemblies are now shared across branches)
                return _handle_assembly_barcode(
                    request, session, assembly, quantity
                )

            # If not an assembly, proceed with regular inventory item
            if request.user.role != "admin":
                # Check if item exists in branch inventory
                branch_inventory = BranchInventory.objects.filter(
                    branch=request.user.branch, inventory__barcode=barcode
                ).first()

                if not branch_inventory:
                    messages.error(
                        request, "Item with this barcode not found in your branch."
                    )
                    return redirect("billing:session_detail", session_id=session.id)

                inventory = branch_inventory.inventory

                # Check actual available quantity (considering session items)
                actual_available = branch_inventory.actual_quantity

                if actual_available < quantity:
                    messages.error(
                        request,
                        f"Not enough stock available. Only {actual_available} units available.",
                    )
                    return redirect("billing:session_detail", session_id=session.id)

            else:
                # Admin can access any inventory
                inventory = Inventory.objects.filter(barcode=barcode).first()

                if not inventory:
                    messages.error(request, "Item with this barcode not found.")
                    return redirect("billing:session_detail", session_id=session.id)

                if inventory.actual_quantity < quantity:
                    messages.error(
                        request,
                        f"Not enough stock available. Only {inventory.actual_quantity} units available.",
                    )
                    return redirect("billing:session_detail", session_id=session.id)

            # Check if item already exists in this session
            existing_item = BillingSessionItem.objects.filter(
                session=session, inventory=inventory
            ).first()

            if existing_item:
                # If item exists, check if adding more quantity is possible
                if request.user.role != "admin":
                    # For non-admin users, check if total quantity (existing + new) doesn't exceed available
                    total_requested = existing_item.quantity + quantity
                    if (
                        branch_inventory.actual_quantity + existing_item.quantity
                        < total_requested
                    ):
                        messages.error(
                            request,
                            f"Cannot add {quantity} more units. Only {branch_inventory.actual_quantity} additional units available.",
                        )
                        return redirect("billing:session_detail", session_id=session.id)

                # Update existing item
                existing_item.quantity += quantity
                existing_item.save()
                messages.success(
                    request,
                    f"Updated quantity to {existing_item.quantity} x {inventory.part_name} in session.",
                )
            else:
                # Create new item
                BillingSessionItem.objects.create(
                    session=session,
                    inventory=inventory,
                    quantity=quantity,
                    price=inventory.discounted_price,
                )
                messages.success(
                    request,
                    f"Added {quantity} x {inventory.part_name} to session.",
                )

        except Inventory.DoesNotExist:
            messages.error(request, "Item with this barcode not found.")
        except ValueError:
            messages.error(request, "Invalid quantity provided.")
        except Exception as e:
            print(e)
            messages.error(request, f"Error: {str(e)}")

    return redirect("billing:session_detail", session_id=session.id)


def _handle_assembly_barcode(request, session, assembly, quantity):
    """
    Helper function to handle assembly barcode scanning.
    Adds all components of the assembly to the billing session.
    Assemblies are shared across all branches, but component availability is branch-specific.
    """
    # Check component availability
    missing_items = []
    for component in assembly.components.all():
        inventory_item = component.inventory_item
        required_qty = component.quantity_required * quantity

        if request.user.role != "admin":
            # For non-admin users, check BranchInventory
            branch_inventory = BranchInventory.objects.filter(
                branch=request.user.branch, inventory=inventory_item
            ).first()

            if not branch_inventory:
                missing_items.append({
                    'item': inventory_item,
                    'required': required_qty,
                    'available': 0,
                    'reason': 'Item not in branch'
                })
            else:
                actual_available = branch_inventory.actual_quantity
                # Check if adding this quantity would exceed available stock
                existing_item = BillingSessionItem.objects.filter(
                    session=session, inventory=inventory_item
                ).first()
                if existing_item:
                    # If item already in session, add its quantity back to available
                    actual_available += existing_item.quantity

                if actual_available < required_qty:
                    missing_items.append({
                        'item': inventory_item,
                        'required': required_qty,
                        'available': branch_inventory.actual_quantity,
                        'reason': 'Insufficient stock'
                    })
        else:
            # For admin users, check inventory directly
            actual_available = inventory_item.actual_quantity
            existing_item = BillingSessionItem.objects.filter(
                session=session, inventory=inventory_item
            ).first()
            if existing_item:
                actual_available += existing_item.quantity

            if actual_available < required_qty:
                missing_items.append({
                    'item': inventory_item,
                    'required': required_qty,
                    'available': inventory_item.actual_quantity,
                    'reason': 'Insufficient stock'
                })

    if missing_items:
        error_msg = f"Cannot add assembly '{assembly.name}'. Missing components:\n"
        for item in missing_items:
            error_msg += f"- {item['item'].part_name}: Required {item['required']}, Available {item['available']} ({item['reason']})\n"
        messages.error(request, error_msg)
        return redirect("billing:session_detail", session_id=session.id)

    # Add all components to the session
    added_items = []
    for component in assembly.components.all():
        inventory_item = component.inventory_item
        component_quantity = component.quantity_required * quantity
        # Use component's selling_price if set, otherwise fall back to inventory item's discounted price
        component_price = component.selling_price if component.selling_price > 0 else inventory_item.discounted_price

        # Check if this component already exists in the session
        existing_item = BillingSessionItem.objects.filter(
            session=session, inventory=inventory_item
        ).first()

        if existing_item:
            # Update existing item - recalculate price based on component price
            existing_item.quantity += component_quantity
            existing_item.price = component_price  # Update to component price
            existing_item.save()
            added_items.append(f"{component_quantity} x {inventory_item.part_name} (updated)")
        else:
            # Create new item with component's selling price
            BillingSessionItem.objects.create(
                session=session,
                inventory=inventory_item,
                quantity=component_quantity,
                price=component_price,
            )
            added_items.append(f"{component_quantity} x {inventory_item.part_name}")

    messages.success(
        request,
        f"Added assembly '{assembly.name}' ({quantity} unit(s)) with components: {', '.join(added_items)}",
    )
    return redirect("billing:session_detail", session_id=session.id)


def delete_item(request, item_id):
    item = get_object_or_404(BillingSessionItem, id=item_id, session__user=request.user)
    if request.method == "POST":
        item.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


def update_item_api(request, item_id):
    item = get_object_or_404(BillingSessionItem, id=item_id, session__user=request.user)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            quantity = data.get("quantity")
            price = data.get("price")

            if quantity is not None and price is not None:
                new_quantity = Decimal(quantity)
                new_price = Decimal(price)

                # Check quantity availability for non-admin users
                if request.user.role != "admin":
                    try:
                        branch_inventory = BranchInventory.objects.get(
                            branch=request.user.branch, inventory=item.inventory
                        )

                        # Check if the new quantity is available (excluding current item)
                        if not branch_inventory.is_quantity_available(
                            new_quantity, exclude_session_item=item
                        ):
                            return JsonResponse(
                                {
                                    "status": "error",
                                    "message": f"Not enough stock available. Only {branch_inventory.actual_quantity} units available.",
                                    "quantity": item.quantity,
                                },
                                status=200,
                            )
                    except BranchInventory.DoesNotExist:
                        return JsonResponse(
                            {
                                "status": "error",
                                "message": "Item not found in your branch inventory.",
                            },
                            status=400,
                        )

                else:
                    if not item.inventory.is_quantity_available(
                        new_quantity, exclude_session_item=item
                    ):
                        return JsonResponse(
                            {
                                "status": "error",
                                "message": "Not enough stock available.",
                                "quantity": item.quantity,
                            },
                            status=200,
                        )

                item.quantity = new_quantity
                item.price = new_price
                item.save()

                return JsonResponse(
                    {
                        "status": "success",
                        "item": {
                            "id": item.id,
                            "quantity": item.quantity,
                            "price": item.price,
                            "amount": float(item.quantity) * float(item.price),
                        },
                    }
                )
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(e)
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@require_GET
def inventory_search_api(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        if request.user.role != "admin":
            # For non-admin users, search in their branch inventory
            branch_inventories = (
                BranchInventory.objects.filter(
                    branch=request.user.branch, inventory__part_name__icontains=q
                )
                | BranchInventory.objects.filter(
                    branch=request.user.branch, inventory__barcode__icontains=q
                )
                | BranchInventory.objects.filter(
                    branch=request.user.branch, inventory__company_name__icontains=q
                )[:20]
            )

            results = [
                {
                    "id": bi.inventory.id,
                    "company_name": bi.inventory.company_name,
                    "part_name": bi.inventory.part_name,
                    "barcode": bi.inventory.barcode,
                    "stock": bi.actual_quantity,  # Use actual available quantity
                }
                for bi in branch_inventories
            ]
        else:
            # For admin users, search all inventory
            items = Inventory.objects.filter(
                Q(part_name__icontains=q)
                | Q(barcode__icontains=q)
                | Q(company_name__icontains=q)
            )[:20]
            results = [
                {
                    "id": item.id,
                    "company_name": item.company_name,
                    "part_name": item.part_name,
                    "barcode": item.barcode,
                    "stock": item.available_quantity,
                }
                for item in items
            ]
    return JsonResponse({"results": results})

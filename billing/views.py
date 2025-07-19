from django.shortcuts import render, redirect, get_object_or_404
from .models import BillingSession, BillingSessionItem
from inventory.models import Inventory
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
        quantity = 1  # Default quantity is 1

        try:
            if request.user.role != "admin":
                data = BranchInventory.objects.filter(
                    branch=request.user.branch, inventory__barcode=barcode
                ).first()
                if data:
                    inventory = data.inventory
                else:
                    messages.error(request, "Item with this barcode not found.")
                    return redirect("billing:session_detail", session_id=session.id)
            else:
                inventory = Inventory.objects.get(barcode=barcode)

                # if 0 < quantity:
                #     messages.error(request, "Not enough stock available.")
                #     pass
                # else:

            item, created = BillingSessionItem.objects.get_or_create(
                session=session,
                inventory=inventory,
                defaults={
                    "quantity": quantity,
                    "price": inventory.discounted_price,
                },
            )
            if not created:
                item.quantity += quantity
                item.save()
            messages.success(
                request,
                f"Added {quantity} x {inventory.part_name} to session.",
            )
        except Inventory.DoesNotExist:
            messages.error(request, "Item with this barcode not found.")
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
                item.quantity = Decimal(quantity)
                item.price = Decimal(price)
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

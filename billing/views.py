from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BillingSession, BillingSessionItem
from inventory.models import Inventory
from django.contrib import messages
from django.http import JsonResponse
import json

# Create your views here.


@login_required
def billing_session_list(request):
    sessions = BillingSession.objects.filter(user=request.user, is_active=True)
    return render(request, "billing/session_list.html", {"sessions": sessions})


@login_required
def billing_session_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            session = BillingSession.objects.create(user=request.user, name=name)
            return redirect("billing:session_detail", session_id=session.id)
        messages.error(request, "Session name is required.")
    return render(request, "billing/session_create.html")


@login_required
def billing_session_detail(request, session_id):
    session = get_object_or_404(
        BillingSession, id=session_id, user=request.user, is_active=True
    )
    items = session.items.select_related("inventory").all()
    return render(
        request, "billing/session_detail.html", {"session": session, "items": items}
    )


@login_required
def add_item_by_barcode(request, session_id):
    session = get_object_or_404(
        BillingSession, id=session_id, user=request.user, is_active=True
    )
    if request.method == "POST":
        barcode = request.POST.get("barcode")
        quantity = 1  # Default quantity is 1
        try:
            inventory = Inventory.objects.get(barcode=barcode)
            if inventory.quantity < quantity:
                messages.error(request, "Not enough stock available.")
            else:
                item, created = BillingSessionItem.objects.get_or_create(
                    session=session,
                    inventory=inventory,
                    defaults={"quantity": quantity, "price": inventory.selling_price},
                )
                if not created:
                    item.quantity += quantity
                    item.save()
                messages.success(
                    request, f"Added {quantity} x {inventory.part_name} to session."
                )
        except Inventory.DoesNotExist:
            messages.error(request, "Item with this barcode not found.")
    return redirect("billing:session_detail", session_id=session.id)


@login_required
def update_items(request, session_id):
    session = get_object_or_404(
        BillingSession, id=session_id, user=request.user, is_active=True
    )
    if request.method == "POST":
        for item in session.items.all():
            quantity = request.POST.get(f"quantity_{item.id}")
            price = request.POST.get(f"price_{item.id}")

            if quantity and price:
                try:
                    item.quantity = int(quantity)
                    item.price = float(price)
                    item.save()
                except (ValueError, TypeError):
                    messages.error(
                        request, f"Invalid values for item {item.inventory.part_name}"
                    )
                    continue

        messages.success(request, "Items updated successfully")
    return redirect("billing:session_detail", session_id=session.id)


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(BillingSessionItem, id=item_id, session__user=request.user)
    if request.method == "POST":
        item.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def update_item_api(request, item_id):
    item = get_object_or_404(BillingSessionItem, id=item_id, session__user=request.user)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            quantity = data.get("quantity")
            price = data.get("price")

            if quantity is not None and price is not None:
                item.quantity = int(quantity)
                item.price = float(price)
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
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

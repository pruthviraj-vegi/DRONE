from django.shortcuts import render
from billing.models import BillingSession
from inventoryManage.models import BranchInventory
from customers.models import Member
from invoice.models import Invoice
from django.db.models import Sum

# Create your views here.


def dashboard(request):
    # get all open sessions
    open_sessions = BillingSession.objects.filter(
        is_active=True, user=request.user
    ).count()
    if request.user.role == "admin":
        total_inventory = BranchInventory.objects.filter(
            inventory__is_active=True
        ).count()
        total_customers = Member.objects.all().count()
        total_sales = Invoice.objects.all().aggregate(total_amount=Sum("total_amount"))[
            "total_amount"
        ]
    else:
        total_inventory = BranchInventory.objects.filter(
            inventory__is_active=True, branch=request.user.branch
        ).count()
        total_customers = Member.objects.filter(branches=request.user.branch).count()
        total_sales = Invoice.objects.filter(sale_user=request.user).aggregate(
            total_amount=Sum("total_amount")
        )["total_amount"]

    context = {
        "open_sessions": open_sessions,
        "total_inventory": total_inventory,
        "total_customers": total_customers,
        "total_sales": total_sales,
    }

    return render(request, "dashboard/dashboard.html", context)

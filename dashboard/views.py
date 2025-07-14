from django.shortcuts import render
from billing.models import BillingSession
from inventoryManage.models import BranchInventory
from customers.models import Member
from invoice.models import Invoice
from django.db.models import Sum
from Drone.decorators import role_required

# Create your views here.


@role_required(allowed_roles=["admin"])
def admin_dashboard(request):
    open_sessions = BillingSession.objects.filter(is_active=True).count()
    total_inventory = BranchInventory.objects.filter().count()
    total_customers = Member.objects.all().count()
    total_sales = Invoice.objects.all().aggregate(total_amount=Sum("total_amount"))[
        "total_amount"
    ]

    context = {
        "open_sessions": open_sessions,
        "total_inventory": total_inventory,
        "total_customers": total_customers,
        "total_sales": total_sales,
        "is_admin": True,
    }
    return render(request, "dashboard/dashboard.html", context)


@role_required(allowed_roles=["manager", "staff"])
def user_dashboard(request):
    open_sessions = BillingSession.objects.filter(
        is_active=True, user=request.user
    ).count()
    total_inventory = BranchInventory.objects.filter(branch=request.user.branch).count()
    total_customers = Member.objects.filter(branches=request.user.branch).count()
    total_sales = Invoice.objects.filter(
        sale_user__branch=request.user.branch
    ).aggregate(total_amount=Sum("total_amount"))["total_amount"]

    context = {
        "open_sessions": open_sessions,
        "total_inventory": total_inventory,
        "total_customers": total_customers,
        "total_sales": total_sales,
        "is_admin": False,
    }
    return render(request, "dashboard/dashboard.html", context)


def dashboard(request):
    if request.user.role == "admin":
        return admin_dashboard(request)
    else:
        return user_dashboard(request)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Member
from .forms import MemberForm

# Create your views here.


def member_list(request):
    # Start with all members
    members = Member.objects.all()

    # Filter by branch if user is not admin
    if request.user.role != "admin":
        members = members.filter(branch=request.user.branch)

    # Search functionality
    search_query = request.GET.get("search", "")

    if search_query:
        members = (
            members.filter(name__icontains=search_query)
            | members.filter(phone__icontains=search_query)
            | members.filter(email__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get("status", "")
    if status_filter:
        members = members.filter(status=status_filter)

    # Pagination
    paginator = Paginator(members, 10)  # Show 10 members per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": Member.STATUS_CHOICES,
    }
    return render(request, "customers/member_list.html", context)


def member_create(request):
    if request.method == "POST":
        form = MemberForm(request.POST, user=request.user)
        if form.is_valid():
            member = form.save()
            messages.success(
                request, f'Member "{member.name}" has been created successfully.'
            )
            return redirect("customers:member_list")
    else:
        form = MemberForm(user=request.user)

    return render(
        request, "customers/member_form.html", {"form": form, "title": "Add New Member"}
    )


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)

    # Check if user has permission to edit this member
    if request.user.role != "admin" and member.branch != request.user.branch:
        messages.error(request, "You don't have permission to edit this member.")
        return redirect("customers:member_list")

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member, user=request.user)
        if form.is_valid():
            member = form.save()
            messages.success(
                request, f'Member "{member.name}" has been updated successfully.'
            )
            return redirect("customers:member_list")
    else:
        form = MemberForm(instance=member, user=request.user)

    return render(
        request,
        "customers/member_form.html",
        {"form": form, "member": member, "title": f"Edit Member: {member.name}"},
    )


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)

    # Check if user has permission to delete this member
    if request.user.role != "admin" and member.branch != request.user.branch:
        messages.error(request, "You don't have permission to delete this member.")
        return redirect("customers:member_list")

    if request.method == "POST":
        name = member.name
        member.delete()
        messages.success(request, f'Member "{name}" has been deleted successfully.')
        return redirect("customers:member_list")

    return render(request, "customers/member_confirm_delete.html", {"member": member})

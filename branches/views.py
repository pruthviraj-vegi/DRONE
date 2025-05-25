from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Branch
from Drone.decorators import admin_required
from django.urls import reverse_lazy


@admin_required
def branch_list(request):
    branches = Branch.objects.all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        branches = branches.filter(name__icontains=search_query) | branches.filter(
            address__icontains=search_query
        )

    # Pagination
    paginator = Paginator(branches, 10)  # Show 10 branches per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
    }
    return render(request, "branches/branch_list.html", context)


@admin_required
def branch_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if name and address and phone and email:
            branch = Branch.objects.create(
                name=name, address=address, phone=phone, email=email
            )
            messages.success(
                request, f'Branch "{branch.name}" has been created successfully.'
            )
            return redirect("branches:branch_list")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, "branches/branch_form.html", {"title": "Create New Branch"})


@admin_required
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if name and address and phone and email:
            branch.name = name
            branch.address = address
            branch.phone = phone
            branch.email = email
            branch.save()
            messages.success(
                request, f'Branch "{branch.name}" has been updated successfully.'
            )
            return redirect("branches:branch_list")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(
        request,
        "branches/branch_form.html",
        {"branch": branch, "title": f"Edit Branch: {branch.name}"},
    )


@admin_required
def branch_delete(request, pk):
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == "POST":
        branch_name = branch.name
        branch.delete()
        messages.success(
            request, f'Branch "{branch_name}" has been deleted successfully.'
        )
        return redirect("branches:branch_list")

    return render(request, "branches/branch_confirm_delete.html", {"branch": branch})

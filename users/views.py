# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import CustomUser, ROLE_CHOICES
from .forms import CustomUserCreationForm, ResetPasswordForm, CustomUserChangeForm
from Drone.decorators import admin_required, role_required
from branches.models import Branch
from django.contrib.auth.decorators import login_required


@role_required(allowed_roles=["admin"])
def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f"User {user.full_name} has been created successfully."
            )
            return redirect("dashboard:dashboard")
    else:
        form = CustomUserCreationForm()

    return render(
        request, "users/create_user.html", {"form": form, "title": "Create New User"}
    )


@role_required(allowed_roles=["admin", "manager"])
def user_list(request):
    # Start with all users
    users = CustomUser.objects.all()

    # Filter by branch if user is not admin
    if request.user.role != "admin":
        users = users.filter(branch=request.user.branch)

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        users = users.filter(full_name__icontains=search_query) | users.filter(
            email__icontains=search_query
        )

    # Role filter
    role_filter = request.GET.get("role", "")
    if role_filter:
        users = users.filter(role=role_filter)

    # Branch filter (only for admin)
    branch_filter = request.GET.get("branch", "")
    if branch_filter and request.user.role == "admin":
        users = users.filter(branch_id=branch_filter)

    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "role_filter": role_filter,
        "branch_filter": branch_filter,
        "branches": Branch.objects.all() if request.user.role == "admin" else None,
        "role_choices": ROLE_CHOICES,
    }
    return render(request, "users/main_page.html", context)


@role_required(allowed_roles=["admin", "manager"])
def user_create(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'User "{user.full_name}" has been created successfully.'
            )
            return redirect("users:user_list")
    else:
        form = CustomUserCreationForm()

    # Filter branch choices based on user role
    if request.user.role != "admin":
        form.fields["branch"].queryset = Branch.objects.filter(
            id=request.user.branch.id
        )
        form.fields["branch"].initial = request.user.branch
        form.fields["branch"].disabled = True

    return render(
        request, "users/create_user.html", {"form": form, "title": "Add New User"}
    )


@role_required(allowed_roles=["admin", "manager"])
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    # Check if user has permission to edit this user
    if request.user.role not in ["admin"] and user.branch != request.user.branch:
        messages.error(request, "You don't have permission to edit this user.")
        return redirect("users:user_list")

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'User "{user.full_name}" has been updated successfully.'
            )
            return redirect("users:user_list")
    else:
        form = CustomUserChangeForm(instance=user)

    # Filter branch choices based on user role
    if request.user.role != "admin":
        form.fields["branch"].queryset = Branch.objects.filter(
            id=request.user.branch.id
        )
        form.fields["branch"].disabled = True

    return render(
        request,
        "users/create_user.html",
        {"form": form, "user": user, "title": f"Edit User: {user.full_name}"},
    )


@role_required(allowed_roles=["admin"])
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    # Check if user has permission to delete this user
    if request.user.role not in ["admin"] and user.branch != request.user.branch:
        messages.error(request, "You don't have permission to delete this user.")
        return redirect("users:user_list")

    if request.method == "POST":
        name = user.full_name
        user.delete()
        messages.success(request, f'User "{name}" has been deleted successfully.')
        return redirect("users:user_list")

    return render(request, "users/user_confirm_delete.html", {"user": user})


@role_required(allowed_roles=["admin"])
def reset_password(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            user.set_password(new_password)
            user.save()
            messages.success(
                request,
                f'Password for user "{user.full_name}" has been reset successfully.',
            )
            return redirect("users:user_list")
    else:
        form = ResetPasswordForm()
    return render(
        request,
        "users/reset_password.html",
        {"form": form, "user": user, "title": f"Reset Password for {user.full_name}"},
    )

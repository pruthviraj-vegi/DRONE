from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Branch
from Drone.decorators import admin_required
from django.urls import reverse_lazy
from .forms import BranchForm
from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator


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


@method_decorator(admin_required, name="dispatch")
class CreateBranch(CreateView):
    model = Branch
    form_class = BranchForm
    template_name = "branches/branch_form.html"
    success_url = reverse_lazy("branches:branch_list")

    def form_valid(self, form):
        messages.success(self.request, "Branch has been created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Branch"
        return context


@method_decorator(admin_required, name="dispatch")
class EditBranch(UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = "branches/branch_form.html"
    success_url = reverse_lazy("branches:branch_list")

    def form_valid(self, form):
        messages.success(self.request, "Branch has been updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Edit Branch: {self.object.name}"
        return context


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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Branch
from Drone.decorators import admin_required
from django.urls import reverse_lazy
from .forms import BranchForm
from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator
from base.utility import get_basic_data
from django.db.models import Q


@admin_required
def branch_list(request):
    template_name = "branches/main_page.html"

    return render(request, template_name)


@admin_required
def fetch_branches(request):

    basic_data = get_basic_data(request)

    query = Q()
    search_query = basic_data["search_query"]
    if search_query:
        query &= Q(name__icontains=search_query) | Q(code__icontains=search_query)

    queryset = Branch.objects.filter(query).order_by(basic_data["sort_column"])
    queryset = queryset[basic_data["start"] : basic_data["start"] + basic_data["limit"]]

    context = {"data": queryset}

    return render(request, "branches/fetch.html", context)


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

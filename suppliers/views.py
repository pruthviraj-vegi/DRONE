from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Supplier
from Drone.decorators import admin_required
from suppliers.forms import SupplierForm
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from base.utility import get_basic_data
from django.db.models import Q

# Create your views here.


@admin_required
def supplier_list(request):
    template_name = "suppliers/main_page.html"

    return render(request, template_name)


@admin_required
def fetch(request):
    basic_data = get_basic_data(request)

    query = Q()

    search_query = basic_data["search_query"]
    if search_query:
        query &= (
            Q(name__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(address__icontains=search_query)
            | Q(tax_number__icontains=search_query)
        )

    queryset = Supplier.objects.filter(query).order_by(basic_data["sort_column"])
    queryset = queryset[basic_data["start"] : basic_data["start"] + basic_data["limit"]]

    context = {
        "data": queryset,
    }
    return render(request, "suppliers/fetch.html", context)


@method_decorator(admin_required, name="dispatch")
class CreateSupplier(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/supplier_form.html"
    success_url = reverse_lazy("suppliers:supplier_list")

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Supplier"
        return context


@method_decorator(admin_required, name="dispatch")
class EditSupplier(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/supplier_form.html"
    success_url = reverse_lazy("suppliers:supplier_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Supplier "{form.instance.name}" has been Updated successfully.',
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Edit Supplier: {self.object.name}"
        return context


@admin_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier_name = supplier.name
        supplier.delete()
        messages.success(
            request, f'Supplier "{supplier_name}" has been deleted successfully.'
        )
        return redirect("suppliers:supplier_list")

    return render(
        request, "suppliers/supplier_confirm_delete.html", {"supplier": supplier}
    )

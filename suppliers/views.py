from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Supplier
from Drone.decorators import admin_required
from suppliers.forms import SupplierForm
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

# Create your views here.


@admin_required
def supplier_list(request):
    suppliers = Supplier.objects.all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        suppliers = (
            suppliers.filter(name__icontains=search_query)
            | suppliers.filter(contact_person__icontains=search_query)
            | suppliers.filter(email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(suppliers, 10)  # Show 10 suppliers per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
    }
    return render(request, "suppliers/supplier_list.html", context)


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

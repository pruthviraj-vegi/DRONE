from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Supplier
from Drone.decorators import admin_required

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


@admin_required
def supplier_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        contact_person = request.POST.get("contact_person")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")
        tax_number = request.POST.get("tax_number")
        registration_number = request.POST.get("registration_number")
        payment_terms = request.POST.get("payment_terms")
        notes = request.POST.get("notes")

        if name and contact_person and phone and email and address:
            supplier = Supplier.objects.create(
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address,
                tax_number=tax_number,
                registration_number=registration_number,
                payment_terms=payment_terms,
                notes=notes,
            )
            messages.success(
                request, f'Supplier "{supplier.name}" has been created successfully.'
            )
            return redirect("suppliers:supplier_list")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(
        request, "suppliers/supplier_form.html", {"title": "Create New Supplier"}
    )


@admin_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        contact_person = request.POST.get("contact_person")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")
        tax_number = request.POST.get("tax_number")
        registration_number = request.POST.get("registration_number")
        payment_terms = request.POST.get("payment_terms")
        notes = request.POST.get("notes")
        is_active = request.POST.get("is_active") == "on"

        if name and contact_person and phone and email and address:
            supplier.name = name
            supplier.contact_person = contact_person
            supplier.phone = phone
            supplier.email = email
            supplier.address = address
            supplier.tax_number = tax_number
            supplier.registration_number = registration_number
            supplier.payment_terms = payment_terms
            supplier.notes = notes
            supplier.is_active = is_active
            supplier.save()

            messages.success(
                request, f'Supplier "{supplier.name}" has been updated successfully.'
            )
            return redirect("suppliers:supplier_list")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(
        request,
        "suppliers/supplier_form.html",
        {"supplier": supplier, "title": f"Edit Supplier: {supplier.name}"},
    )


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

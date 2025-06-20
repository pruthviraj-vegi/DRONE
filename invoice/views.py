from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from billing.models import BillingSession
from customers.models import Member
from invoice.models import Invoice, InvoiceItem
from .forms import InvoiceForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

# Create your views here.


def select_details(request, session_id):
    session = get_object_or_404(BillingSession, id=session_id, is_active=True)
    items = session.items.select_related("inventory").all()
    total_amount = sum(item.amount for item in items)
    form = InvoiceForm(initial={"total_amount": total_amount}, user=request.user)

    if total_amount <= 0:
        messages.error(request, "Total amount must be greater than 0")
        return redirect("billing:session_detail", session_id=session.id)

    if request.method == "POST":
        form = InvoiceForm(request.POST, user=request.user)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.sale_user = request.user
            invoice.save()

        for item in items:
            InvoiceItem.objects.create(
                invoice=invoice,
                inventory=item.inventory,
                purchased_price=item.inventory.purchased_price,
                quantity=item.quantity,
                price=item.price,
            )
        session.delete()
        messages.success(request, "Invoice created and session closed.")
        return redirect("billing:session_list")

    return render(
        request,
        "invoice/select_details.html",
        {
            "form": form,
        },
    )


def invoice_list(request):
    invoices = Invoice.objects.filter(sale_user=request.user).order_by("-id")
    return render(request, "invoice/invoice_list.html", {"invoices": invoices})


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.select_related("inventory").all()
    return render(
        request, "invoice/invoice_detail.html", {"invoice": invoice, "items": items}
    )


class InvoiceEditView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "invoice/select_details.html"
    success_url = reverse_lazy("invoice:invoice_list")
    pk_url_kwarg = "invoice_id"

    def get_queryset(self):
        return Invoice.objects.filter(
            sale_user=self.request.user, id=self.kwargs["invoice_id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoice"] = self.get_object()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "invoice:invoice_detail", kwargs={"invoice_id": self.object.id}
        )

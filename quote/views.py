from django.shortcuts import render, redirect, get_object_or_404
from .models import QuoteSession, QuoteMember, QuoteInventory, QuoteItem
from .forms import (
    QuoteMemberForm,
    QuoteInventoryForm,
    QuoteItemAddForm,
    QuoteSessionForm,
)
from django.views.generic.edit import CreateView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.forms import formset_factory


# Create your views here.
def get_quote_session(request):
    template_name = "quote/main_page.html"
    quote_session = QuoteSession.objects.all().order_by("status", "-created_at")
    return render(request, template_name, {"quote_session": quote_session})


class QuoteSessionCreateView(CreateView):
    model = QuoteSession
    form_class = QuoteSessionForm
    template_name = "quote/session_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["show_status"] = False  # Hide status field on create
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("quote:session_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Session"
        return context


class QuoteSessionUpdateView(UpdateView):
    model = QuoteSession
    form_class = QuoteSessionForm
    template_name = "quote/session_form.html"

    def get_success_url(self):
        return reverse("quote:session_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Session"
        return context


class QuoteDetails(View):
    template_name = "quote/session_detail.html"

    def get(self, request, pk):
        session = get_object_or_404(QuoteSession, pk=pk)
        items = session.quote_items_session.all()
        active_inventory = QuoteInventory.objects.filter(status="active")
        # Map inventory_id to QuoteItem for quick lookup
        item_map = {item.quote_inventory_id: item for item in items}
        initial_data = []
        for inv in active_inventory:
            if inv.id in item_map:
                initial_data.append(
                    {
                        "inventory_id": inv.id,
                        "quantity": item_map[inv.id].quantity,
                        "price": item_map[inv.id].price,
                    }
                )
            else:
                initial_data.append(
                    {
                        "inventory_id": inv.id,
                        "quantity": 0,
                        "price": inv.price,
                    }
                )
        QuoteItemAddFormSet = formset_factory(QuoteItemAddForm, extra=0)
        formset = QuoteItemAddFormSet(initial=initial_data)
        form_inventory_pairs = zip(formset.forms, active_inventory)
        context = {
            "session": session,
            "items": items,
            "active_inventory": active_inventory,
            "formset": formset,
            "form_inventory_pairs": form_inventory_pairs,
        }
        return render(
            request,
            self.template_name,
            context,
        )

    def post(self, request, pk):
        session = get_object_or_404(QuoteSession, pk=pk)
        items = session.quote_items_session.all()
        active_inventory = QuoteInventory.objects.filter(status="active")
        item_map = {item.quote_inventory_id: item for item in items}
        QuoteItemAddFormSet = formset_factory(QuoteItemAddForm, extra=0)
        formset = QuoteItemAddFormSet(request.POST)
        form_inventory_pairs = zip(formset.forms, active_inventory)
        try:
            if formset.is_valid():
                for idx, form in enumerate(formset):
                    if not form.has_changed():
                        continue
                    quantity = form.cleaned_data.get("quantity")
                    price = form.cleaned_data.get("price")
                    inventory_id = form.cleaned_data.get("inventory_id")
                    if inventory_id in item_map:
                        # Update existing QuoteItem
                        quote_item = item_map[inventory_id]
                        quote_item.quantity = quantity
                        quote_item.price = price
                        quote_item.save()
                    else:
                        # Create new QuoteItem if quantity > 0
                        if quantity and quantity > 0:
                            quote_inventory = QuoteInventory.objects.get(
                                id=inventory_id
                            )
                            QuoteItem.objects.create(
                                quote_session=session,
                                quote_inventory=quote_inventory,
                                quantity=quantity,
                                price=price,
                            )
                # Recalculate total
                total = sum(
                    item.quantity * item.price
                    for item in session.quote_items_session.all()
                )
                session.total_amount = total
                session.save()

                session.status = "sent"
                session.save()

                return redirect(reverse("quote:session_detail", kwargs={"pk": pk}))
            else:
                items = session.quoteitem_set.select_related("quote_inventory").all()
                return render(
                    request,
                    self.template_name,
                    {
                        "formset": formset,
                        "session": session,
                        "form_inventory_pairs": form_inventory_pairs,
                        "formset_errors": formset.errors,
                        "items": items,
                        "active_inventory": active_inventory,
                    },
                )
        except Exception as e:
            items = session.quoteitem_set.select_related("quote_inventory").all()
            return render(
                request,
                self.template_name,
                {
                    "formset": formset,
                    "session": session,
                    "form_inventory_pairs": form_inventory_pairs,
                    "formset_errors": formset.errors,
                    "items": items,
                    "active_inventory": active_inventory,
                },
            )


def get_quote_member(request):
    template_name = "quote/member_page.html"
    quote_member = QuoteMember.objects.all()
    return render(request, template_name, {"quote_member": quote_member})


class QuoteMemberCreateView(CreateView):
    model = QuoteMember
    form_class = QuoteMemberForm
    template_name = "quote/member_form.html"
    success_url = reverse_lazy("quote:member_page")

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Member"
        return context


class QuoteMemberUpdateView(UpdateView):
    model = QuoteMember
    form_class = QuoteMemberForm
    template_name = "quote/member_form.html"
    success_url = reverse_lazy("quote:member_page")

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Member"
        return context


def get_quote_inventory(request):
    template_name = "quote/inventory_page.html"
    quote_inventory = QuoteInventory.objects.all()
    return render(request, template_name, {"quote_inventory": quote_inventory})


class QuoteInventoryCreateView(CreateView):
    model = QuoteInventory
    form_class = QuoteInventoryForm
    template_name = "quote/inventory_form.html"
    success_url = reverse_lazy("quote:inventory_page")

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Inventory"
        return context


class QuoteInventoryUpdateView(UpdateView):
    model = QuoteInventory
    form_class = QuoteInventoryForm
    template_name = "quote/inventory_form.html"
    success_url = reverse_lazy("quote:inventory_page")

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Inventory"
        return context

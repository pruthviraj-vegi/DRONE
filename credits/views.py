from django.shortcuts import render, redirect, get_object_or_404
from .models import Credit
from .forms import CreditForm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Value, F, Max
from django.utils import timezone
from customers.models import Member
from invoice.models import Invoice
from django.contrib import messages


def get_credit_filtration(request, is_limit=True):
    today_date = timezone.now()

    # 1. Consolidate parameter parsing
    params = {
        "limit": 20,
        "start": 0,
        "min_value": 0,
        "max_value": 0,
        "sort_column": "name",
        "sort_order": None,
    }

    try:
        params.update(
            {
                "limit": int(request.GET.get("limit", 20)),
                "start": int(request.GET.get("start", 0)),
                "min_value": int(request.GET.get("min_value", 0)),
                "max_value": int(request.GET.get("max_value", 0)),
                "sort_column": request.GET.get("sort_column", "name"),
                "sort_order": request.GET.get("sort_type"),
            }
        )
    except ValueError:
        pass

    # 2. Build search filters once
    search_term = request.GET.get("search", "")
    filters = {
        field: request.GET.get(field, "") for field in ["name", "address", "phone"]
    }

    # 3. Optimize query building
    def build_search_filter(prefix):
        base_filter = Q()
        if search_term:
            base_filter |= (
                Q(**{f"{prefix}__name__icontains": search_term})
                | Q(**{f"{prefix}__address__icontains": search_term})
                | Q(**{f"{prefix}__phone__icontains": search_term})
            )

        for field, value in filters.items():
            if value:
                base_filter &= Q(**{f"{prefix}__{field}__icontains": value})
        return base_filter

    # 4. Execute queries with optimized filters
    credits = Credit.objects.filter(build_search_filter("member"))
    invoice_members = Invoice.objects.filter(invoice_type=False).filter(
        build_search_filter("customer")
    )

    # 5. Use select_related to reduce queries
    member_ids = set(credits.values_list("member_id", flat=True)).union(
        set(invoice_members.values_list("customer_id", flat=True))
    )

    # 6. Fetch members in a single query with all needed fields
    members = Member.objects.filter(id__in=member_ids)

    members_dict = {
        m.id: {
            "id": m.id,
            "name": m.name,
            "address": m.address,
            "phone": m.phone,
            "credit": 0,
            "debit": 0,
            "balance": 0,
            "recent_paid": 0,
        }
        for m in members
    }

    # 7. Optimize aggregation queries
    transactions = credits.values("member__id").annotate(
        credit=Sum("amount", filter=Q(paid=False), default=Value(0)),
        debit=Sum("amount", filter=Q(paid=True), default=Value(0)),
        balance=F("credit") - F("debit"),
        recent_paid=Max("created_at", filter=Q(paid=True)),
    )

    # 8. Update members data efficiently
    for t in transactions:
        member_id = t["member__id"]
        if member_id in members_dict:
            members_dict[member_id].update(
                {
                    "credit": t["credit"],
                    "debit": t["debit"],
                    "balance": t["balance"],
                    "recent_paid": (
                        (today_date - t["recent_paid"]).days if t["recent_paid"] else 0
                    ),
                }
            )

    invoices = invoice_members.values("customer__id").annotate(
        credit=Sum("total_amount", default=Value(0)),
        debit=Sum("advance_amount", default=Value(0)),
        balance=F("credit") - F("debit"),
    )

    # 9. Update invoice data efficiently
    for invoice in invoices:
        member_id = invoice["customer__id"]
        if member_id in members_dict:
            member = members_dict[member_id]
            member["credit"] += invoice["credit"]
            member["debit"] += invoice["debit"]
            member["balance"] += invoice["balance"]

    # 10. Efficient sorting
    result = sorted(members_dict.values(), key=lambda x: x["name"])

    credits = sorted(
        result,
        key=lambda x: x[params["sort_column"]],
        reverse=params["sort_order"] != "Dec",
    )

    if params["min_value"] > 0 or params["max_value"] > 0:
        credits = [
            credit
            for credit in credits
            if (
                params["min_value"] <= abs(credit["balance"])
                and (
                    params["max_value"] == 0
                    or abs(credit["balance"]) <= params["max_value"]
                )
            )
        ]

    if is_limit:
        credits = credits[params["start"] : params["start"] + params["limit"]]

    return credits


def IndividualBalance(pk):
    transactions = Credit.objects.filter(member=pk).values("paid", "amount")

    invoices = Invoice.objects.filter(customer__id=pk, invoice_type=False).values(
        "invoice_type", "total_amount", "advance_amount"
    )

    bill = invoices.aggregate(
        balance=Sum("total_amount", default=Value(0))
        - Sum("advance_amount", default=Value(0))
    )["balance"]

    mem = transactions.aggregate(
        balance=Sum("amount", filter=Q(paid=False), default=Value(0))
        - Sum("amount", filter=Q(paid=True), default=Value(0))
    )["balance"]

    return float(bill) + float(mem)


def individualDetails(pk):
    # Retrieve transactions and invoices separately without sorting
    transactions = Credit.objects.filter(member=pk).values(
        "id", "member__name", "paid", "amount", "notes", "created_at"
    )

    invoices = Invoice.objects.filter(customer__id=pk, invoice_type=False).values(
        "id",
        "customer__name",
        "invoice_type",
        "total_amount",
        "advance_amount",
        "notes",
        "created_at",
    )

    trans = []

    for value in transactions:
        data = {
            "id": value["id"],
            "name": str(value["member__name"]),
            "model": "transaction",
            "paid": "Paid" if value["paid"] else "Purchased",
            "amount": value["amount"],
            "notes": value["notes"],
            "created_at": value["created_at"],
        }
        trans.append(data)

    for value in invoices:
        data = {
            "id": value["id"],
            "name": str(value["customer__name"]),
            "model": "invoice",
            "paid": "Purchased",
            "amount": value["total_amount"] - value["advance_amount"],
            "notes": "Inv No : #" + str(value["id"]),
            "created_at": value["created_at"],
        }
        trans.append(data)

    bill = invoices.aggregate(
        balance=Sum("total_amount", default=Value(0))
        - Sum("advance_amount", default=Value(0))
    )["balance"]

    mem = transactions.aggregate(
        balance=Sum("amount", filter=Q(paid=False), default=Value(0))
        - Sum("amount", filter=Q(paid=True), default=Value(0))
    )["balance"]

    return sorted(trans, key=lambda item: item["created_at"], reverse=True), bill + mem


def credit_list(request):
    return render(request, "credits/main_page.html")


def fetch_credits(request):
    credits = get_credit_filtration(request)
    return render(request, "credits/fetch.html", {"data": credits})


class create_credit(CreateView):
    model = Credit
    form_class = CreditForm
    template_name = "credits/form.html"
    success_url = reverse_lazy("credits:credit_page")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # If you want to set a user field on the model, do it here
        # form.instance.user = self.request.user
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Credit"
        return context


def credit_details(request, pk):
    member = get_object_or_404(Member, id=pk)
    context = {
        "members": member,
        "title": "Credit Details",
        "balance": IndividualBalance(pk),
    }
    return render(request, "credits/individual/main_page.html", context)


def fetchIndividualCredits(request, pk):
    template = "credits/individual/fetch.html"
    limit = request.GET.get("limit", 20)
    start = request.GET.get("start", 0)

    transactions, balance = individualDetails(pk)

    context = {"data": transactions[int(start) : int(start) + int(limit)]}

    return render(request, template, context)


class create_credit_individual(CreateView):
    model = Credit
    form_class = CreditForm
    template_name = "credits/individual/form.html"
    success_url = reverse_lazy("credits:credit_details")
    pk_url_kwarg = "pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["include_member"] = False
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.member = Member.objects.get(id=self.kwargs["pk"])
        messages.success(self.request, "Credit added successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Credit"
        return context

    def get_success_url(self):
        return reverse_lazy(
            "credits:credit_details", kwargs={"pk": self.object.member.id}
        )


class edit_credit_individual(UpdateView):
    model = Credit
    form_class = CreditForm
    template_name = "credits/individual/form.html"
    success_url = reverse_lazy("credits:credit_details")
    pk_url_kwarg = "pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["include_member"] = False
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Credit updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Credit"
        return context

    def get_success_url(self):
        return reverse_lazy(
            "credits:credit_details", kwargs={"pk": self.object.member.id}
        )


class delete_credit_individual(DeleteView):
    model = Credit
    success_url = reverse_lazy("credits:credit_page")
    pk_url_kwarg = "pk"
    template_name = "credits/individual/credit_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "credits:credit_details", kwargs={"pk": self.object.member.id}
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Credit deleted successfully")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Delete Credit"
        return context

    def get_queryset(self):
        return Credit.objects.filter(created_by=self.request.user)


class edit_credit(UpdateView):
    model = Credit
    form_class = CreditForm
    template_name = "credits/form.html"
    success_url = reverse_lazy("credits:credit_page")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Credit"
        return context

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Member
from .forms import MemberForm
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

# Create your views here.


def member_list(request):
    # Start with all members
    members = Member.objects.all()

    # Filter by branch if user is not admin
    if request.user.role != "admin":
        members = members.filter(branches=request.user.branch)

    # Search functionality
    search_query = request.GET.get("search", "")

    if search_query:
        members = members.filter(name__icontains=search_query) | members.filter(
            phone__icontains=search_query
        )

    # Status filter
    status_filter = request.GET.get("status", "")
    if status_filter:
        members = members.filter(status=status_filter)

    # Pagination
    paginator = Paginator(members, 10)  # Show 10 members per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": Member.STATUS_CHOICES,
    }
    return render(request, "customers/main_page.html", context)


class CreateCustomer(CreateView):
    model = Member
    form_class = MemberForm
    template_name = "customers/form.html"
    success_url = reverse_lazy("customers:member_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Member"
        return context


class EditCustomer(UpdateView):
    model = Member
    form_class = MemberForm
    template_name = "customers/form.html"
    success_url = reverse_lazy("customers:member_list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Permission check
        if (
            request.user.role != "admin"
            and request.user.branch not in self.object.branches.all()
        ):
            messages.error(request, "You don't have permission to edit this member.")
            return redirect("customers:member_list")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to form
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Member "{self.object.name}" has been updated successfully.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = self.object
        context["title"] = f"Edit Member: {self.object.name}"
        return context


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)

    # Check if user has permission to delete this member
    if (
        request.user.role != "admin"
        and request.user.branch not in member.branches.all()
    ):
        messages.error(request, "You don't have permission to delete this member.")
        return redirect("customers:member_list")

    if request.method == "POST":
        name = member.name
        member.delete()
        messages.success(request, f'Member "{name}" has been deleted successfully.')
        return redirect("customers:member_list")

    return render(request, "customers/delete.html", {"member": member})

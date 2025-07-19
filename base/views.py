from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from users.forms import CustomLoginForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from base.utility import Suggestion
from django.http import JsonResponse


# Create your views here.
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "base/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard:dashboard")


def logout_view(request):
    logout(request)
    return redirect("base:login")


def SuggestionAddress(request):
    suggestion = Suggestion()
    return suggestion.get_address()


def SuggestionCompanyName(request):
    search_name = request.GET.get("search_name")
    suggestion = Suggestion()
    return suggestion.get_company_name(search_name)

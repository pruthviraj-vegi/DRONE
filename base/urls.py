from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = "base"

urlpatterns = [
    path("", lambda request: redirect("/dashboard/", permanent=False)),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]

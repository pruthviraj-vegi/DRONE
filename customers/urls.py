from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("", views.member_list, name="member_list"),
    path("fetch/", views.fetch_members, name="fetch_members"),
    path("create/", views.CreateCustomer.as_view(), name="member_create"),
    path("<int:pk>/edit/", views.EditCustomer.as_view(), name="member_edit"),
    path("<int:pk>/delete/", views.member_delete, name="member_delete"),
]

from django.urls import path
from . import views

app_name = "branches"

urlpatterns = [
    path("", views.branch_list, name="branch_list"),
    path("create/", views.branch_create, name="branch_create"),
    path("<int:pk>/edit/", views.branch_edit, name="branch_edit"),
    path("<int:pk>/delete/", views.branch_delete, name="branch_delete"),
]

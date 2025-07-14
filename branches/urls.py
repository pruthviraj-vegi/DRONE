from django.urls import path
from . import views

app_name = "branches"

urlpatterns = [
    path("", views.branch_list, name="branch_list"),
    path("fetch/", views.fetch_branches, name="fetch_branches"),
    path("create/", views.CreateBranch.as_view(), name="branch_create"),
    path("<int:pk>/edit/", views.EditBranch.as_view(), name="branch_edit"),
    path("<int:pk>/delete/", views.branch_delete, name="branch_delete"),
]

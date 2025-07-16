from django.urls import path
from . import views

app_name = "credits"

urlpatterns = [
    path("", views.credit_list, name="credit_page"),
    path("fetch/", views.fetch_credits, name="fetch_credits"),
    path("create/", views.create_credit.as_view(), name="create_credit"),
    path("details/<int:pk>/", views.credit_details, name="credit_details"),
    path(
        "fetch-individual/<int:pk>/",
        views.fetchIndividualCredits,
        name="fetch_individual_credits",
    ),
    path(
        "create-individual/<int:pk>/",
        views.create_credit_individual.as_view(),
        name="create_credit_individual",
    ),
    path(
        "edit-individual/<int:pk>/",
        views.edit_credit_individual.as_view(),
        name="edit_credit_individual",
    ),
    path(
        "delete-individual/<int:pk>/",
        views.delete_credit_individual.as_view(),
        name="delete_credit_individual",
    ),
]

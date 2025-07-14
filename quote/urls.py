from django.urls import path
from . import views

app_name = "quote"

urlpatterns = [
    path("", views.get_quote_session, name="quote_page"),
    path(
        "create/", views.QuoteSessionCreateView.as_view(), name="create_quote_session"
    ),
    path(
        "update/<int:pk>/",
        views.QuoteSessionUpdateView.as_view(),
        name="update_quote_session",
    ),
    path("session/<int:pk>/", views.QuoteDetails.as_view(), name="session_detail"),
    ## member
    path("members/", views.get_quote_member, name="member_page"),
    path(
        "members/create/", views.QuoteMemberCreateView.as_view(), name="member_create"
    ),
    path(
        "members/update/<int:pk>/",
        views.QuoteMemberUpdateView.as_view(),
        name="member_update",
    ),
    ## inventory
    path("inventory/", views.get_quote_inventory, name="inventory_page"),
    path(
        "inventory/create/",
        views.QuoteInventoryCreateView.as_view(),
        name="inventory_create",
    ),
    path(
        "inventory/update/<int:pk>/",
        views.QuoteInventoryUpdateView.as_view(),
        name="inventory_update",
    ),
]

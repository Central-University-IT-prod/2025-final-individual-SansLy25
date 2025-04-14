from django.urls import path
from clients import views

urlpatterns = [
    path(
        "bulk",
        views.ClientMassCreateUpdateView.as_view(),
        name="client-bulk",
    ),
    path(
        "<uuid:clientId>",
        views.ClientRetrieveView.as_view(),
        name="client-retrieve",
    ),
]

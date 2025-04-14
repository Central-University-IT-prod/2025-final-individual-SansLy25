from django.urls import path, include
from advertisers import views
from core.routers import NoTrailingSlashRouter

router = NoTrailingSlashRouter()
router.register(r"campaigns", views.CampaignViewSet, basename="campaigns")

urlpatterns = [
    path("<uuid:advertiserId>/", include(router.urls)),
    path(
        "<uuid:advertiserId>",
        views.AdvertiserRetrieveAPIView.as_view(),
        name="advertiser-detail",
    ),
    path(
        "bulk",
        views.AdvertiserMassCreateUpdateAPIView.as_view(),
        name="advertiser-detail",
    ),
]

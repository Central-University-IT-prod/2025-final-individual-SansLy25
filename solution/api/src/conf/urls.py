from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from clients.views import MlScoreCreateUpdateView, AdRetrieveView, AdClickView
from core.views import DateSetView
from conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("advertisers/", include("advertisers.urls")),
    path("clients/", include("clients.urls")),
    path("stats", include("stats.urls")),
    path("ml-scores", MlScoreCreateUpdateView.as_view(), name="ml-scores"),
    path("time/advance", DateSetView.as_view(), name="time-advance"),
    path("ads", AdRetrieveView.as_view(), name="ads"),
    path("ads/<uuid:adId>/click", AdClickView.as_view(), name="ads-click"),
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path(
        "redoc",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

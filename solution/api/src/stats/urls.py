from django.urls import path
from stats.views import (
    CampaignStatsSingleView,
    AdvertiserStatsView,
    CampaignStatsSingleDailyView,
    AdvertiserStatsDailyView,
)

urlpatterns = [
    path(
        "/campaigns/<uuid:campaignId>",
        CampaignStatsSingleView.as_view(),
        name="campaign-stats-single",
    ),
    path(
        "/advertisers/<uuid:advertiserId>/campaigns",
        AdvertiserStatsView.as_view(),
        name="advertiser-stats",
    ),
    path(
        "/campaigns/<uuid:campaignId>/daily",
        CampaignStatsSingleDailyView.as_view(),
        name="campaign-stats-single-daily",
    ),
    path(
        "/advertisers/<uuid:advertiserId>/daily",
        AdvertiserStatsDailyView.as_view(),
        name="advertiser-stats-daily",
    ),
]

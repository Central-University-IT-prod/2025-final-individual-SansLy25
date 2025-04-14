from collections import defaultdict

from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    GenericAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from clients.models import AdClick, AdImpression
from advertisers.models import Campaign, Advertiser
from stats.serializers import StatsSerializer, StatsDailySerializer


class CampaignStatsSingleView(GenericAPIView):
    queryset = Campaign.objects.all()
    lookup_url_kwarg = "campaignId"
    serializer_class = StatsSerializer

    def get_stats(self):
        spent_impressions = 0
        spent_clicks = 0
        campaign = self.get_object()
        clicks = AdClick.objects.filter(campaign=campaign)
        impressions = AdImpression.objects.filter(campaign=campaign)

        for click in clicks:
            spent_clicks += click.cost
        for impression in impressions:
            spent_impressions += impression.cost

        return {
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks,
            "spent_total": spent_impressions + spent_clicks,
            "impressions_count": impressions.count(),
            "clicks_count": clicks.count(),
            "conversion": (
                (clicks.count() / impressions.count()) * 100
                if impressions.count()
                else 0
            ),
        }

    def get(self, request, *args, **kwargs):
        stats = self.get_stats()
        serializer = self.get_serializer(data=stats)
        serializer.is_valid(raise_exception=False)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CampaignStatsSingleDailyView(GenericAPIView):
    serializer_class = StatsDailySerializer
    queryset = Campaign.objects.all()
    lookup_url_kwarg = "campaignId"

    def get_queryset(self):
        campaign_id = self.kwargs.get("campaignId")
        return Campaign.objects.filter(pk=campaign_id)

    def get_stats(self):
        campaigns = self.get_queryset()

        daily_stats = defaultdict(
            lambda: {
                "impressions_count": 0,
                "clicks_count": 0,
                "spent_impressions": 0,
                "spent_clicks": 0,
                "spent_total": 0,
                "conversion": 0,
            }
        )

        clicks = AdClick.objects.filter(campaign__in=campaigns)
        impressions = AdImpression.objects.filter(campaign__in=campaigns)

        for click in clicks:
            date = click.created_at
            daily_stats[date]["clicks_count"] += 1
            daily_stats[date]["spent_clicks"] += click.cost
            daily_stats[date]["spent_total"] += click.cost

        for impression in impressions:
            date = impression.created_at
            daily_stats[date]["impressions_count"] += 1
            daily_stats[date]["spent_impressions"] += impression.cost
            daily_stats[date]["spent_total"] += impression.cost

        for date, stats in daily_stats.items():
            if stats["impressions_count"] > 0:
                stats["conversion"] = (
                    stats["clicks_count"] / stats["impressions_count"]
                ) * 100
            else:
                stats["conversion"] = 0

        result = [{**stats, "date": date} for date, stats in daily_stats.items()]

        return result

    def get(self, request, *args, **kwargs):
        stats = self.get_stats()
        serializer = self.get_serializer(data=stats, many=True)
        serializer.is_valid(raise_exception=False)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AdvertiserStatsView(CampaignStatsSingleView):
    queryset = Advertiser.objects.all()
    lookup_url_kwarg = "advertiserId"
    serializer_class = StatsSerializer

    def get_stats(self):
        advertiser = self.get_object()
        campaigns = Campaign.objects.filter(advertiser=advertiser)
        total_spent_impressions = 0
        total_spent_clicks = 0
        total_impressions_count = 0
        total_clicks_count = 0

        for campaign in campaigns:
            clicks = AdClick.objects.filter(campaign=campaign)
            impressions = AdImpression.objects.filter(campaign=campaign)

            for click in clicks:
                total_spent_clicks += click.cost
            for impression in impressions:
                total_spent_impressions += impression.cost

            total_impressions_count += impressions.count()
            total_clicks_count += clicks.count()

        total_spent = total_spent_impressions + total_spent_clicks
        conversion = (
            (total_clicks_count / total_impressions_count) * 100
            if total_impressions_count
            else 0
        )

        return {
            "spent_impressions": total_spent_impressions,
            "spent_clicks": total_spent_clicks,
            "spent_total": total_spent,
            "impressions_count": total_impressions_count,
            "clicks_count": total_clicks_count,
            "conversion": conversion,
        }


class AdvertiserStatsDailyView(CampaignStatsSingleDailyView):
    queryset = Advertiser.objects.all()
    lookup_url_kwarg = "advertiserId"

    def get_queryset(self):
        advertiser_id = self.kwargs.get("advertiserId")
        advertiser = get_object_or_404(Advertiser, pk=advertiser_id)
        return Campaign.objects.filter(advertiser=advertiser)

from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from advertisers.models import Advertiser, Campaign
from advertisers.serializers import (
    AdvertiserSerializer,
    CampaignSerializer,
)
from core.views import BulkCreateUpdateAPIView
from conf.settings import MULTI_PART_DATA_FOR_CAMPAIGN


class AdvertiserRetrieveAPIView(RetrieveAPIView):
    queryset = Advertiser.objects.all()
    lookup_url_kwarg = "advertiserId"
    serializer_class = AdvertiserSerializer


class AdvertiserMassCreateUpdateAPIView(BulkCreateUpdateAPIView):
    serializer_class = AdvertiserSerializer
    pk_field_name = "advertiser_id"


class CampaignViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    lookup_url_kwarg = "campaignId"
    serializer_class = CampaignSerializer
    if MULTI_PART_DATA_FOR_CAMPAIGN:
        parser_classes = [MultiPartParser]

    def get_queryset(self):
        advertiser_id = self.kwargs["advertiserId"]
        advertiser = get_object_or_404(Advertiser, pk=advertiser_id)
        return Campaign.objects.filter(advertiser=advertiser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["advertiser_id"] = self.kwargs["advertiserId"]
        return context

    def get_paginated_response(self, data):
        return Response(data)

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "advertiser_id": self.kwargs["advertiserId"],
        }

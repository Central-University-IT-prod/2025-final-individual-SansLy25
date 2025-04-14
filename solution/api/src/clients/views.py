from django.db.models import Exists, OuterRef, F, Value, FloatField, Q, Max, Case, When
from django.db.models.functions import Coalesce
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    RetrieveAPIView,
    CreateAPIView,
    get_object_or_404,
    GenericAPIView,
)
from rest_framework.response import Response
from rest_framework import status

from advertisers.models import Advertiser, Campaign
from clients.serializers import (
    ClientAdSerializer,
    MLScoreCreateSerializer,
    ClientSerializer,
    AdClickSerializer,
)
from clients.models import Client, MLScore, AdClick, AdImpression
from core.models import CurrentDate
from core.views import BulkCreateUpdateAPIView


class ClientMassCreateUpdateView(BulkCreateUpdateAPIView):
    pk_field_name = "client_id"
    serializer_class = ClientSerializer


class ClientRetrieveView(RetrieveAPIView):
    queryset = Client.objects.all()
    lookup_url_kwarg = "clientId"
    serializer_class = ClientSerializer


class AdRetrieveView(RetrieveAPIView):
    serializer_class = ClientAdSerializer

    def get_queryset(self):
        client_id = self.request.query_params.get("client_id")
        client = get_object_or_404(Client, pk=client_id)
        today_date = CurrentDate.get_today()

        campaigns = Campaign.objects.filter(
            Q(start_date__lte=today_date) & Q(end_date__gte=today_date),
            Q(targeting__age_from__lte=client.age)
            | Q(targeting__age_from__isnull=True),
            Q(targeting__age_to__gte=client.age) | Q(targeting__age_to__isnull=True),
            Q(targeting__location=client.location)
            | Q(targeting__location__isnull=True),
            Q(targeting__gender=client.gender)
            | Q(targeting__gender__isnull=True)
            | Q(targeting__gender="ALL"),
            Q(impressions_count__lte=F("impressions_limit") * 1.049),
            Q(clicks_count__lte=F("clicks_limit") * 1.049),
        )

        if not campaigns.exists():
            raise Http404

        return campaigns

    def get_object(self):
        client_id = self.request.query_params.get("client_id")
        client = get_object_or_404(Client, pk=client_id)

        ad_clicks = AdClick.objects.filter(client=client)
        ml_scores = MLScore.objects.filter(client=client)
        ad_impressions = AdImpression.objects.filter(client=client)

        campaigns = self.get_queryset().annotate(
            impressed=Exists(ad_impressions.filter(campaign=OuterRef("pk"))),
            clicked=Exists(ad_clicks.filter(campaign=OuterRef("pk"))),
            ml_score=Coalesce(
                ml_scores.filter(advertiser=OuterRef("advertiser")).values("score")[:1],
                Value(0),
                output_field=FloatField(),
            ),
        )

        campaigns = campaigns.annotate(
            profit=Coalesce(
                F("cost_per_click")
                * Case(
                    When(clicked=True, then=Value(0)),
                    default=Value(1),
                    output_field=FloatField(),
                )
                + F("cost_per_impression")
                * Case(
                    When(impressed=True, then=Value(0)),
                    default=Value(1),
                    output_field=FloatField(),
                ),
                Value(0),
                output_field=FloatField(),
            ),
            completion=Coalesce(
                Value(0.5)
                * (
                    Value(1)
                    - Case(
                        When(clicks_limit=0, then=Value(0)),
                        default=F("clicks_count") * (1.0001 / F("clicks_limit")),
                        output_field=FloatField(),
                    )
                )
                * Case(
                    When(clicked=True, then=Value(0)),
                    default=Value(1),
                    output_field=FloatField(),
                )
                + Value(0.5)
                * (
                    Value(1)
                    - Case(
                        When(impressions_limit=0, then=Value(0)),
                        default=F("impressions_count")
                        * (1.0001 / F("impressions_limit")),
                        output_field=FloatField(),
                    )
                )
                * Case(
                    When(impressed=True, then=Value(0)),
                    default=Value(1),
                    output_field=FloatField(),
                ),
                Value(0),
                output_field=FloatField(),
            ),
        )

        max_values = campaigns.aggregate(
            max_profit=Coalesce(Max("profit"), Value(0), output_field=FloatField()),
            max_ml_score=Coalesce(Max("ml_score"), Value(0), output_field=FloatField()),
            max_completion=Coalesce(
                Max("completion"), Value(0), output_field=FloatField()
            ),
        )

        campaigns = campaigns.annotate(
            norm_profit=Case(
                When(profit=0, then=Value(0)),
                default=F("profit") / Value(max_values["max_profit"]),
                output_field=FloatField(),
            ),
            norm_ml_score=Case(
                When(ml_score=0, then=Value(0)),
                default=F("ml_score") / Value(max_values["max_ml_score"]),
                output_field=FloatField(),
            ),
            norm_completion=Case(
                When(completion=0, then=Value(0)),
                default=F("completion") / (1.001 * Value(max_values["max_completion"])),
                output_field=FloatField(),
            ),
            final_score=(F("norm_ml_score") * 0.1)
            + (F("norm_completion") * 0.2)
            + (F("norm_profit") * 0.7),
        ).order_by("-final_score")

        best_ad = campaigns.first()
        if not best_ad:
            raise ValidationError()

        if not best_ad.impressed:
            AdImpression.objects.create(
                campaign=best_ad, client=client, cost=best_ad.cost_per_impression
            )
            best_ad.impressions_count += 1
            best_ad.save()

        return best_ad

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="client_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="UUID клиента",
                required=True,
            ),
        ],
        responses={200: None},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdClickView(GenericAPIView):
    queryset = Campaign.objects.all()
    serializer_class = AdClickSerializer
    lookup_url_kwarg = "adId"

    def post(self, request, *args, **kwargs):
        ad = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = get_object_or_404(Client, pk=serializer.validated_data["client_id"])
        if AdImpression.objects.filter(client=client, campaign=ad).exists():
            if not AdClick.objects.filter(client=client, campaign=ad).exists():
                AdClick.objects.create(
                    client=client, campaign=ad, cost=ad.cost_per_click
                )
                ad.clicks_count += 1
                ad.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MlScoreCreateUpdateView(CreateAPIView):
    serializer_class = MLScoreCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        get_object_or_404(Client, pk=request.data.get("client_id"))
        get_object_or_404(Advertiser, pk=request.data.get("advertiser_id"))

        self.perform_create(serializer)

        return Response(status=status.HTTP_201_CREATED)

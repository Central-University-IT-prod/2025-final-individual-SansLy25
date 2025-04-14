from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from advertisers.serializers import CampaignImageSerializer
from advertisers.models import Advertiser, Campaign
from clients.models import Client, MLScore
from conf.settings import MULTI_PART_DATA_FOR_CAMPAIGN
from core.serializers import NotNullModelSerializerMixin


class ClientSerializer(NotNullModelSerializerMixin, serializers.ModelSerializer):
    client_id = serializers.UUIDField(source="id")

    class Meta:
        model = Client
        fields = [
            "login",
            "age",
            "location",
            "gender",
            "client_id",
        ]


class ClientAdSerializer(NotNullModelSerializerMixin, serializers.ModelSerializer):
    ad_id = serializers.UUIDField(source="id")
    advertiser_id = serializers.UUIDField(source="advertiser.id")
    if MULTI_PART_DATA_FOR_CAMPAIGN:
        images = CampaignImageSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = ["ad_id", "ad_title", "ad_text", "advertiser_id"]
        if MULTI_PART_DATA_FOR_CAMPAIGN:
            fields.append("images")

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if MULTI_PART_DATA_FOR_CAMPAIGN:
            if "images" in repr:
                images = []
                for image in repr["images"]:
                    images.append(image["image"])

                repr["images"] = images

        return repr


class MLScoreCreateSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField()
    advertiser_id = serializers.UUIDField()

    class Meta:
        model = MLScore
        fields = ["client_id", "advertiser_id", "score"]

    def create(self, validated_data):

        score = validated_data.pop("score")

        client = get_object_or_404(Client, pk=validated_data.pop("client_id"))
        advertiser = get_object_or_404(
            Advertiser, pk=validated_data.pop("advertiser_id")
        )

        existed_ml_score = MLScore.objects.filter(client=client, advertiser=advertiser)

        if existed_ml_score.exists():
            return existed_ml_score.update(score=score)

        return MLScore.objects.create(client=client, advertiser=advertiser, score=score)


class AdClickSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()

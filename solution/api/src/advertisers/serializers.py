from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from advertisers.models import Advertiser, Campaign, Target, CampaignImage
from conf.settings import MULTI_PART_DATA_FOR_CAMPAIGN
from core.models import CurrentDate
from core.serializers import NotNullModelSerializerMixin
from advertisers.llm_integration import generate_ad_text, moderate
from conf import settings


class AdvertiserSerializer(serializers.ModelSerializer):
    advertiser_id = serializers.UUIDField(source="id")

    class Meta:
        model = Advertiser
        fields = ["advertiser_id", "name"]


class TargetSerializer(NotNullModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Target
        exclude = ["id"]

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        self.validate_age(attrs.get("age_from", None), attrs.get("age_to", None))
        return validated_data

    def validate_age(self, age_from, age_to):
        if (not age_from is None and not age_to is None) and age_from > age_to:
            raise serializers.ValidationError("The age_from cannot be more than age_to")


class CampaignImageSerializer(serializers.ModelSerializer):
    image = serializers.FileField()

    class Meta:
        model = CampaignImage
        fields = ["image"]


class CampaignSerializer(NotNullModelSerializerMixin, serializers.ModelSerializer):
    campaign_id = serializers.UUIDField(source="id", read_only=True)
    advertiser_id = serializers.PrimaryKeyRelatedField(
        source="advertiser", read_only=True
    )
    targeting = TargetSerializer(required=False)
    description_prompt = serializers.CharField(required=False, allow_blank=True)
    moderate_ad_text = serializers.BooleanField(required=False)

    if MULTI_PART_DATA_FOR_CAMPAIGN:
        images = CampaignImageSerializer(many=True, read_only=True)
        uploaded_images = serializers.ListField(
            child=serializers.ImageField(allow_empty_file=False, allow_null=True),
            required=False,
            write_only=True,
        )

    class Meta:
        model = Campaign
        fields = [
            "campaign_id",
            "advertiser_id",
            "impressions_limit",
            "clicks_limit",
            "cost_per_impression",
            "cost_per_click",
            "ad_title",
            "ad_text",
            "start_date",
            "end_date",
            "targeting",
            "description_prompt",
            "moderate_ad_text",
        ]

        if MULTI_PART_DATA_FOR_CAMPAIGN:
            fields += ["images", "uploaded_images"]

        extra_kwargs = {
            "ad_text": {"required": False},
            "start_date": {"required": False},
            "end_date": {"required": False},
            "impressions_limit": {"required": False},
            "clicks_limit": {"required": False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field, (serializers.IntegerField, serializers.FloatField)):
                field.validators.append(MinValueValidator(0))

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if MULTI_PART_DATA_FOR_CAMPAIGN:
            if "images" in repr:
                images = []
                for image in repr["images"]:
                    images.append(image["image"])

                repr["images"] = images

        return repr

    def validate_start_date(self, start_date):
        today = CurrentDate.get_today()
        if start_date < today:
            raise serializers.ValidationError("The start_date cannot be before today")
        return start_date

    def validate_end_date(self, end_date):
        today = CurrentDate.get_today()
        if end_date < today:
            raise serializers.ValidationError("The end_date cannot be before today")
        return end_date

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        update_not_required_fields = [
            "start_date",
            "end_date",
            "impressions_limit",
            "clicks_limit",
        ]
        for field_name in update_not_required_fields:
            field = validated_data.get(field_name, None)
            if self.instance is None:
                if field is None:
                    raise serializers.ValidationError(
                        f"{field_name} this field is required"
                    )
            else:
                if (
                    field is not None
                ) and self.instance.start_date <= CurrentDate.get_today():
                    raise serializers.ValidationError(
                        f"{field_name} this field is not editable ufter campaign start"
                    )

        if ("ad_text" in validated_data) == ("description_prompt" in validated_data):
            raise serializers.ValidationError(
                "You specified ad_text along "
                "with description_prompt or"
                " you did not specify any of these"
            )
        if "description_prompt" in validated_data:
            company = get_object_or_404(Advertiser, id=self.context["advertiser_id"])
            text, correct = generate_ad_text(
                validated_data["description_prompt"],
                validated_data["ad_title"],
                company.name,
            )
            if not correct:
                raise serializers.ValidationError("Your description prompt is invalid")

            validated_data["ad_text"] = text
            validated_data.pop("description_prompt")

        optional_moderation = validated_data.pop("moderate_ad_text", False)

        if "ad_text" in validated_data and (
            settings.MODERATE_AD_TEXT or optional_moderation
        ):
            moderation = moderate(validated_data["ad_text"])
            if not moderation["passed"]:
                raise serializers.ValidationError(moderation["detail"])

        return validated_data

    def create(self, validated_data):
        targeting_data = validated_data.pop("targeting", None)
        advertiser_id = self.context["advertiser_id"]
        advertiser = get_object_or_404(Advertiser, id=advertiser_id)

        if targeting_data:
            targeting_serializer = TargetSerializer(data=targeting_data)
            if not targeting_serializer.is_valid():
                raise serializers.ValidationError(
                    {"targeting": targeting_serializer.errors}
                )
            targeting = targeting_serializer.save()
            validated_data["targeting"] = targeting

        images = None
        if MULTI_PART_DATA_FOR_CAMPAIGN:
            images = validated_data.pop("uploaded_images", None)

        campaign = Campaign.objects.create(advertiser=advertiser, **validated_data)
        if images is not None:
            for image in images:
                CampaignImage.objects.create(campaign=campaign, image=image)

        return campaign

    def update(self, instance, validated_data):
        targeting_data = validated_data.pop("targeting", None)
        images_data = validated_data.pop("images", [])

        if targeting_data:
            targeting_instance = instance.targeting
            if targeting_instance:
                targeting_serializer = TargetSerializer(
                    targeting_instance, data=targeting_data
                )
            else:
                targeting_serializer = TargetSerializer(data=targeting_data)

            if not targeting_serializer.is_valid():
                raise serializers.ValidationError(
                    {"targeting": targeting_serializer.errors}
                )
            targeting = targeting_serializer.save()
            instance.targeting = targeting

        instance = super().update(instance, validated_data)
        instance.images.all().delete()

        for image_data in images_data:
            CampaignImage.objects.create(campaign=instance, **image_data)
        return instance

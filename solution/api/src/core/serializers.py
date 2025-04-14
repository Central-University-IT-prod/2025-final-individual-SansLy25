from rest_framework import serializers
from core.models import CurrentDate


class NotNullModelSerializerMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            key: value
            for key, value in representation.items()
            if value is not None and value != []
        }


class CurrentDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentDate
        fields = ["current_date"]

    def create(self, validated_data):
        CurrentDate.objects.all().delete()
        return super().create(validated_data)

from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    spent_impressions = serializers.FloatField()
    spent_clicks = serializers.FloatField()
    spent_total = serializers.FloatField()
    impressions_count = serializers.IntegerField()
    clicks_count = serializers.IntegerField()
    conversion = serializers.FloatField()


class StatsDailySerializer(StatsSerializer):
    date = serializers.IntegerField()

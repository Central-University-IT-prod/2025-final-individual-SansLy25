import uuid

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CurrentDate(UUIDModel):
    current_date = models.IntegerField()

    @classmethod
    def get_today(cls):
        dates = cls.objects.all()
        today = dates.first().current_date if dates.exists() else 0
        return today

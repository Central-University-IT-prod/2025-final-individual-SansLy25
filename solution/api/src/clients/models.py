from django.db import models

from core.models import UUIDModel, CurrentDate
from advertisers.models import Advertiser, Campaign


class Client(UUIDModel):
    login = models.CharField("Логин", max_length=300)
    age = models.IntegerField("Возраст")
    location = models.CharField("Местоположение", max_length=300)
    gender = models.CharField(
        "Пол",
        max_length=300,
        choices=(("MALE", "Male"), ("FEMALE", "Female"), ("ALL", "All")),
    )


class MLScore(UUIDModel):
    advertiser = models.ForeignKey(
        Advertiser, on_delete=models.CASCADE, verbose_name="Рекламодатель"
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    score = models.IntegerField("Оценка ML")


class AdClick(UUIDModel):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, verbose_name="Реклама"
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    created_at = models.IntegerField(default=CurrentDate.get_today)
    cost = models.IntegerField()


class AdImpression(UUIDModel):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, verbose_name="Реклама"
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    created_at = models.IntegerField(default=CurrentDate.get_today)
    cost = models.IntegerField()

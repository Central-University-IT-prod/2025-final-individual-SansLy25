from django.db import models

from core.models import UUIDModel


class Advertiser(UUIDModel):
    name = models.CharField(max_length=350)


class Target(UUIDModel):
    gender = models.CharField(
        "Пол аудитории",
        max_length=350,
        choices=(("MALE", "Male"), ("FEMALE", "Female"), ("ALL", "All")),
        null=True,
        blank=True,
    )
    age_from = models.IntegerField(
        "Мин. возраст аудитории",
        null=True,
        blank=True,
    )
    age_to = models.IntegerField(
        "Макс. возраст аудитории",
        null=True,
        blank=True,
    )
    location = models.CharField(
        "Локация аудитории",
        max_length=350,
        null=True,
        blank=True,
    )


class Campaign(UUIDModel):
    impressions_limit = models.IntegerField("Лимит показов")
    clicks_limit = models.IntegerField("Лимит переходов")
    cost_per_impression = models.FloatField("Стоимость одного показа")
    clicks_count = models.IntegerField("Количество кликов", default=0)
    impressions_count = models.IntegerField("Количество показов", default=0)
    cost_per_click = models.FloatField("Стоимость одного клика")
    ad_title = models.CharField("Название", max_length=350)
    ad_text = models.TextField("Текст объявления")
    start_date = models.IntegerField("День начала показа")
    end_date = models.IntegerField("Ден окончания показа")
    targeting = models.OneToOneField(
        Target,
        related_name="campaign",
        on_delete=models.CASCADE,
        verbose_name="Настройки таргетинга",
        null=True,
        blank=True,
    )
    advertiser = models.ForeignKey(
        Advertiser,
        related_name="campaigns",
        verbose_name="Рекламодатель",
        on_delete=models.CASCADE,
    )


class CampaignImage(UUIDModel):
    image = models.ImageField(
        "Изображения",
        upload_to="campaign_images/",
    )
    campaign = models.ForeignKey(
        Campaign,
        related_name="images",
        on_delete=models.CASCADE,
        verbose_name="Объявление",
    )

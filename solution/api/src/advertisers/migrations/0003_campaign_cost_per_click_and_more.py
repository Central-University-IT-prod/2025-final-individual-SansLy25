# Generated by Django 5.1.6 on 2025-02-13 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("advertisers", "0002_target_alter_advertiser_name_campaign"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="cost_per_click",
            field=models.FloatField(default=0, verbose_name="Стоимость одного клика"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="campaign",
            name="cost_per_impression",
            field=models.FloatField(verbose_name="Стоимость одного показа"),
        ),
    ]

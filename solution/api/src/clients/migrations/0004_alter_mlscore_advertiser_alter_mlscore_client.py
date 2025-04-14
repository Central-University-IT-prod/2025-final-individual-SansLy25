# Generated by Django 5.1.6 on 2025-02-16 02:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("advertisers", "0004_campaign_click_count_campaign_impression_count"),
        ("clients", "0003_alter_client_age_alter_client_gender_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mlscore",
            name="advertiser",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="advertisers.advertiser"
            ),
        ),
        migrations.AlterField(
            model_name="mlscore",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="clients.client"
            ),
        ),
    ]

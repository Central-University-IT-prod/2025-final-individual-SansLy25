from django.test import TestCase
from django.core.exceptions import ValidationError

from advertisers.models import Advertiser, Campaign
from clients.models import Client, MLScore, AdClick, AdImpression


class ClientModelTest(TestCase):
    def test_client_creation(self):
        client = Client.objects.create(
            login="test_user", age=25, location="Moscow", gender="MALE"
        )
        self.assertEqual(client.login, "test_user")
        self.assertEqual(client.age, 25)
        self.assertEqual(client.location, "Moscow")
        self.assertEqual(client.gender, "MALE")

    def test_client_gender_choices(self):
        client = Client(
            login="test_user", age=25, location="Moscow", gender="INVALID_GENDER"
        )
        with self.assertRaises(ValidationError):
            client.full_clean()  # Проверка валидации


class MLScoreModelTest(TestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.client = Client.objects.create(
            login="test_user", age=25, location="Moscow", gender="MALE"
        )

    def test_mlscore_creation(self):
        ml_score = MLScore.objects.create(
            advertiser=self.advertiser, client=self.client, score=85
        )
        self.assertEqual(ml_score.advertiser, self.advertiser)
        self.assertEqual(ml_score.client, self.client)
        self.assertEqual(ml_score.score, 85)


class AdClickModelTest(TestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.campaign = Campaign.objects.create(
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=2.0,
            ad_title="Test Campaign",
            ad_text="This is a test campaign",
            start_date=20231001,
            end_date=20231031,
            advertiser=self.advertiser,
        )
        self.client = Client.objects.create(
            login="test_user", age=25, location="Moscow", gender="MALE"
        )

    def test_adclick_creation(self):
        ad_click = AdClick.objects.create(
            campaign=self.campaign, client=self.client, cost=10
        )
        self.assertEqual(ad_click.campaign, self.campaign)
        self.assertEqual(ad_click.client, self.client)
        self.assertEqual(ad_click.cost, 10)


class AdImpressionModelTest(TestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.campaign = Campaign.objects.create(
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=2.0,
            ad_title="Test Campaign",
            ad_text="This is a test campaign",
            start_date=20231001,
            end_date=20231031,
            advertiser=self.advertiser,
        )
        self.client = Client.objects.create(
            login="test_user", age=25, location="Moscow", gender="MALE"
        )

    def test_adimpression_creation(self):
        ad_impression = AdImpression.objects.create(
            campaign=self.campaign, client=self.client, cost=5
        )
        self.assertEqual(ad_impression.campaign, self.campaign)
        self.assertEqual(ad_impression.client, self.client)
        self.assertEqual(ad_impression.cost, 5)

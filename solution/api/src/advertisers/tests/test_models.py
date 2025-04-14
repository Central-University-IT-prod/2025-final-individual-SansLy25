import os

from django.test import TestCase
from advertisers.models import Advertiser, Target, Campaign, CampaignImage
from django.core.files.uploadedfile import SimpleUploadedFile


class AdvertiserModelTest(TestCase):
    def test_create_advertiser(self):
        advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.assertEqual(advertiser.name, "Test Advertiser")


class TargetModelTest(TestCase):
    def test_create_target(self):
        target = Target.objects.create(
            gender="MALE", age_from=18, age_to=35, location="New York"
        )
        self.assertEqual(target.gender, "MALE")
        self.assertEqual(target.age_from, 18)
        self.assertEqual(target.age_to, 35)
        self.assertEqual(target.location, "New York")

    def test_target_gender_choices(self):
        valid_genders = dict(Target._meta.get_field("gender").choices).keys()
        self.assertIn("MALE", valid_genders)
        self.assertIn("FEMALE", valid_genders)
        self.assertIn("ALL", valid_genders)


class CampaignModelTest(TestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.target = Target.objects.create(
            gender="ALL", age_from=20, age_to=50, location="USA"
        )

    def test_create_campaign(self):
        campaign = Campaign.objects.create(
            impressions_limit=1000,
            clicks_limit=500,
            cost_per_impression=0.05,
            cost_per_click=0.1,
            ad_title="Test Campaign",
            ad_text="This is a test campaign.",
            start_date=1,
            end_date=30,
            targeting=self.target,
            advertiser=self.advertiser,
        )
        self.assertEqual(campaign.impressions_limit, 1000)
        self.assertEqual(campaign.clicks_limit, 500)
        self.assertEqual(campaign.cost_per_impression, 0.05)
        self.assertEqual(campaign.cost_per_click, 0.1)
        self.assertEqual(campaign.ad_title, "Test Campaign")
        self.assertEqual(campaign.ad_text, "This is a test campaign.")
        self.assertEqual(campaign.start_date, 1)
        self.assertEqual(campaign.end_date, 30)
        self.assertEqual(campaign.targeting, self.target)
        self.assertEqual(campaign.advertiser, self.advertiser)


class CampaignImageModelTest(TestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.target = Target.objects.create(
            gender="ALL", age_from=20, age_to=50, location="USA"
        )
        self.campaign = Campaign.objects.create(
            impressions_limit=1000,
            clicks_limit=500,
            cost_per_impression=0.05,
            cost_per_click=0.1,
            ad_title="Test Campaign",
            ad_text="This is a test campaign.",
            start_date=1,
            end_date=30,
            targeting=self.target,
            advertiser=self.advertiser,
        )

    def test_create_campaign_image(self):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        self.campaign_image = CampaignImage.objects.create(
            image=image, campaign=self.campaign
        )
        self.assertTrue(self.campaign_image.image)
        self.assertEqual(self.campaign_image.campaign, self.campaign)

    def tearDown(self):
        if hasattr(self, "campaign_image") and self.campaign_image.image:
            if os.path.isfile(self.campaign_image.image.path):
                os.remove(self.campaign_image.image.path)

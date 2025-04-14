from rest_framework.test import APITestCase
from rest_framework import status
from advertisers.models import Advertiser, Campaign, Target


class CampaignViewSetTestCase(APITestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.advertiser_id = self.advertiser.id
        self.base_url = f"/advertisers/{self.advertiser_id}/campaigns"

    def test_create_campaign_success(self):
        data = {
            "impressions_limit": 1000,
            "clicks_limit": 100,
            "cost_per_impression": 0.5,
            "cost_per_click": 5,
            "ad_title": "Test Campaign",
            "ad_text": "This is a test campaign",
            "start_date": 1609459200,
            "end_date": 1609545600,
            "targeting": {
                "gender": "MALE",
                "age_from": 20,
                "age_to": 30,
                "location": "New York",
            },
        }
        response = self.client.post(self.base_url, data, format="json")
        campaign = Campaign.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campaign.objects.count(), 1)
        self.assertEqual(campaign.ad_title, "Test Campaign")
        self.assertEqual(campaign.impressions_limit, data["impressions_limit"])
        self.assertEqual(campaign.clicks_limit, data["clicks_limit"])
        self.assertEqual(campaign.cost_per_impression, data["cost_per_impression"])
        self.assertEqual(campaign.cost_per_click, data["cost_per_click"])
        self.assertEqual(campaign.ad_text, data["ad_text"])
        self.assertEqual(campaign.ad_title, data["ad_title"])
        self.assertEqual(campaign.start_date, data["start_date"])
        self.assertEqual(campaign.end_date, data["end_date"])
        self.assertEqual(campaign.targeting.gender, data["targeting"]["gender"])
        self.assertEqual(campaign.targeting.age_from, data["targeting"]["age_from"])
        self.assertEqual(campaign.targeting.age_to, data["targeting"]["age_to"])
        self.assertEqual(campaign.targeting.location, data["targeting"]["location"])

    def test_create_campaign_validation_errors(self):
        invalid_data = [
            {
                "impressions_limit": -1,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 5,
                "ad_title": "Test",
                "ad_text": "Test",
                "start_date": 2,
                "end_date": 10,
            },
            {
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 5,
                "ad_title": "Test",
                "ad_text": "Test",
                "start_date": 2,
                "end_date": 10,
                "targeting": {"gender": "MALE", "age_from": 30, "age_to": 20},
            },
            {
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 5,
                "ad_title": "Test",
                "ad_text": "Test",
                "start_date": 2,
                "end_date": 10,
                "targeting": {"gender": "INVALID", "age_from": 20, "age_to": 30},
            },
        ]

        for data in invalid_data:
            with self.subTest(invalid_data=data):
                response = self.client.post(self.base_url, data, format="json")
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST, data
                )

    def test_retrieve_campaign_not_found(self):
        non_existent_campaign_id = "00000000-0000-0000-0000-000000000000"
        url = f"{self.base_url}{non_existent_campaign_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_campaign_not_found(self):
        non_existent_campaign_id = "00000000-0000-0000-0000-000000000000"
        url = f"/{self.base_url}{non_existent_campaign_id}/"
        data = {"ad_title": "Updated Campaign"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_campaign_not_found(self):
        non_existent_campaign_id = "00000000-0000-0000-0000-000000000000"
        url = f"/{self.base_url}{non_existent_campaign_id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_campaign_missing_required_fields(self):
        data = {
            "impressions_limit": 1000,
            "clicks_limit": 100,
        }
        response = self.client.post(self.base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cost_per_impression", response.data)

    def test_create_missing_update_not_required_fields(self):
        invalid_data = {
            "clicks_limit": 34,
            "cost_per_impression": 23.0,
            "cost_per_click": 41.0,
            "ad_title": "strings",
            "ad_text": "strings",
            "start_date": 0,
            "end_date": 10,
            "targeting": {
                "gender": "MALE",
                "age_from": 2,
                "age_to": 12,
                "location": "string",
            },
        }

        response = self.client.post(self.base_url, invalid_data, format="json")
        self.assertEqual(response.status_code, 400)
        invalid_data["impressions_limit"] = 20
        response = self.client.post(self.base_url, invalid_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_update_campaign_invalid_data(self):
        campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=5,
            ad_title="Test Campaign",
            ad_text="This is a test campaign",
            start_date=1609459200,
            end_date=1609545600,
        )

        url = f"{self.base_url}/{campaign.id}"
        invalid_data = {
            "impressions_limit": -1,
            "start_date": 1609545600,
            "end_date": 1609459200,
        }
        response = self.client.put(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_valid(self):
        campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=5,
            ad_title="Test Campaign",
            ad_text="This is a test campaign",
            start_date=5,
            end_date=10,
        )
        data = {
            "impressions_limit": 12,
            "clicks_limit": 34,
            "cost_per_impression": 23.0,
            "cost_per_click": 41.0,
            "ad_title": "strings",
            "ad_text": "strings",
            "start_date": 0,
            "end_date": 10,
            "targeting": {
                "gender": "MALE",
                "age_from": 2,
                "age_to": 12,
                "location": "string",
            },
        }

        url = f"{self.base_url}/{campaign.id}"
        response = self.client.put(url, data, format="json")
        data["advertiser_id"] = self.advertiser.id
        data["campaign_id"] = str(campaign.id)

        response_data = response.data
        self.assertEqual(response_data, data)

    def test_update_after_campaign_start(self):
        self.client.post("/time/advance", {"current_date": "6"}, format="json")
        campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            impressions_limit=1000.0,
            clicks_limit=100.0,
            cost_per_impression=0.5,
            cost_per_click=5,
            ad_title="Test Campaign",
            ad_text="This is a test campaign",
            start_date=5,
            end_date=10,
        )
        data = {
            "impressions_limit": 12,
            "clicks_limit": 34,
            "cost_per_impression": 23.0,
            "cost_per_click": 41.0,
            "ad_title": "strings",
            "ad_text": "strings",
            "start_date": 6,
            "end_date": 10,
        }
        url = f"{self.base_url}/{campaign.id}"
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.client.post("/time/advance", {"current_date": "4"}, format="json")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_delete_campaign(self):
        campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=5,
            ad_title="Test Campaign",
            ad_text="This is a test campaign",
            start_date=2,
            end_date=10,
        )
        url = f"{self.base_url}/{campaign.id}"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Campaign.objects.count(), 0)

    def test_list_campaigns_pagination_success(self):

        for i in range(1, 20):
            Campaign.objects.create(
                advertiser=self.advertiser,
                impressions_limit=1000,
                clicks_limit=100,
                cost_per_impression=0.5,
                cost_per_click=5,
                ad_title=f"Test Campaign {i}",
                ad_text="This is a test campaign",
                start_date=1609459200,
                end_date=1609545600,
            )

        response = self.client.get(self.base_url, {"page": 2, "size": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        for i, campaign in enumerate(response.data, start=6):
            self.assertEqual(f"Test Campaign {i}", campaign["ad_title"])

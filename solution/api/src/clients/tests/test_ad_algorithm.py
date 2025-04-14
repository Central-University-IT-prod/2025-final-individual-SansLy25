import uuid
from rest_framework.test import APITestCase

from advertisers.models import Campaign, Advertiser


class TargetingTestCase(APITestCase):
    def setUp(self):
        response_advertisers = self.client.post(
            "/advertisers/bulk",
            [
                {"advertiser_id": str(uuid.uuid4()), "name": "advertiser_1"},
                {"advertiser_id": str(uuid.uuid4()), "name": "advertiser_2"},
            ],
            format="json",
        ).data

        self.advertiser_1 = response_advertisers[0]
        self.advertiser_2 = response_advertisers[1]

        self.clients = self.client.post(
            "/clients/bulk",
            [
                {
                    "client_id": str(uuid.uuid4()),
                    "login": "client",
                    "age": 23,
                    "location": "A",
                    "gender": "FEMALE",
                },
                {
                    "client_id": str(uuid.uuid4()),
                    "login": "client",
                    "age": 40,
                    "location": "M",
                    "gender": "FEMALE",
                },
                {
                    "client_id": str(uuid.uuid4()),
                    "login": "client",
                    "age": 45,
                    "location": "B",
                    "gender": "MALE",
                },
            ],
            format="json",
        ).data

        self.first_client = self.clients[0]
        self.second_client = self.clients[1]
        self.third_client = self.clients[2]

    def create_campaign(
        self,
        advertiser,
        cost_per_impression=0,
        cost_per_click=0,
        impressions_limit=0,
        clicks_limit=0,
    ):
        return Campaign.objects.create(
            ad_text="text",
            ad_title="title",
            advertiser=Advertiser.objects.get(id=advertiser["advertiser_id"]),
            cost_per_click=cost_per_click,
            cost_per_impression=cost_per_impression,
            impressions_limit=impressions_limit,
            clicks_limit=clicks_limit,
            start_date=0,
            end_date=0,
        )

    def set_ml_score(self, advertiser, client, score):
        self.client.post(
            "/ml-scores",
            data={
                "advertiser_id": advertiser["advertiser_id"],
                "client_id": client["client_id"],
                "score": score,
            },
        )

    def test_best_ml_score_choice(self):
        self.create_campaign(self.advertiser_1, impressions_limit=47, clicks_limit=12)
        campaign2 = self.create_campaign(
            self.advertiser_2, impressions_limit=47, clicks_limit=12
        )

        self.set_ml_score(self.advertiser_1, self.first_client, 8)
        self.set_ml_score(self.advertiser_2, self.first_client, 5)
        self.set_ml_score(self.advertiser_1, self.first_client, 2)

        response = self.client.get(
            f"/ads?client_id={self.first_client['client_id']}"
        ).data
        self.assertEqual(response["ad_id"], str(campaign2.id))

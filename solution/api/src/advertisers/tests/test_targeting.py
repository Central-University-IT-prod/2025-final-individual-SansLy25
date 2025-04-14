import uuid
from rest_framework.test import APITestCase

from advertisers.models import Campaign


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
                    "age": 25,
                    "location": "New mexico",
                    "gender": "MALE",
                },
                {
                    "client_id": str(uuid.uuid4()),
                    "login": "client",
                    "age": 40,
                    "location": "Syberia",
                    "gender": "FEMALE",
                },
                {
                    "client_id": str(uuid.uuid4()),
                    "login": "client",
                    "age": 45,
                    "location": "Syberia",
                    "gender": "MALE",
                },
            ],
            format="json",
        ).data

        self.male_client = self.clients[0]
        self.female_client = self.clients[1]
        self.third_client = self.clients[2]

    def create_campaign(self, advertiser, start_date=0, end_date=0, targeting=None):
        data = {
            "impressions_limit": 12,
            "clicks_limit": 12,
            "cost_per_impression": 0,
            "cost_per_click": 0,
            "ad_title": "string",
            "ad_text": "string",
            "start_date": start_date,
            "end_date": end_date,
        }

        if targeting is not None:
            data["targeting"] = targeting

        response = self.client.post(
            f"/advertisers/{advertiser['advertiser_id']}/campaigns",
            data=data,
            format="json",
        )
        return response.data

    def set_date(self, date):
        self.client.post("/time/advance", {"current_date": date})

    def get_ad_response(self, user):
        return self.client.get(f"/ads?client_id={user['client_id']}", format="json")

    def test_male_client_sees_male_and_all_campaigns(self):
        self.create_campaign(self.advertiser_2, targeting={"gender": "FEMALE"})
        campaign_male = self.create_campaign(
            self.advertiser_2, targeting={"gender": "MALE"}
        )
        campaign_all = self.create_campaign(
            self.advertiser_1, targeting={"gender": "ALL"}
        )

        response = self.get_ad_response(self.male_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ad_id"], campaign_male["campaign_id"])
        Campaign.objects.filter(targeting__gender__in=["MALE"]).delete()
        response = self.get_ad_response(self.male_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ad_id"], campaign_all["campaign_id"])
        Campaign.objects.filter(targeting__gender__in=["ALL"]).delete()
        self.assertEqual(Campaign.objects.all().count(), 1)

        response = self.get_ad_response(self.male_client)
        self.assertEqual(response.status_code, 404)

    def test_female_client_sees_female_and_all_campaigns(self):
        self.create_campaign(self.advertiser_2, targeting={"gender": "MALE"})
        campaign_female = self.create_campaign(
            self.advertiser_2, targeting={"gender": "FEMALE"}
        )
        campaign_all = self.create_campaign(
            self.advertiser_1, targeting={"gender": "ALL"}
        )

        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ad_id"], campaign_female["campaign_id"])
        Campaign.objects.filter(targeting__gender__in=["FEMALE"]).delete()
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ad_id"], campaign_all["campaign_id"])
        Campaign.objects.filter(targeting__gender__in=["ALL"]).delete()
        self.assertEqual(Campaign.objects.all().count(), 1)
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 404)

    def test_not_started_company_not_visible(self):
        self.set_date(5)
        self.create_campaign(self.advertiser_1, 10, 20)
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 404)

    def test_ended_company_not_visible(self):
        self.set_date(10)
        self.create_campaign(self.advertiser_1, 10, 20)
        self.set_date(25)
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 404)

    def test_started_company_visible(self):
        self.set_date(5)
        self.create_campaign(self.advertiser_2, 5, 5)
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 200)

    def test_age_from_targeting_into_range(self):
        self.create_campaign(self.advertiser_1, targeting={"age_from": 40})
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 200)

    def test_age_from_targeting_not_into_range(self):
        self.create_campaign(self.advertiser_1, targeting={"age_from": 40})
        response = self.get_ad_response(self.male_client)
        self.assertEqual(response.status_code, 404)

    def test_age_to_targeting_into_range(self):
        self.create_campaign(self.advertiser_1, targeting={"age_to": 25})
        response = self.get_ad_response(self.male_client)
        self.assertEqual(response.status_code, 200)

    def test_age_to_targeting_not_into_range(self):
        self.create_campaign(self.advertiser_1, targeting={"age_to": 25})
        response = self.get_ad_response(self.female_client)
        self.assertEqual(response.status_code, 404)

    def test_complex_age_targeting(self):
        campaign_20_30 = self.create_campaign(
            self.advertiser_1, targeting={"age_from": 20, "age_to": 30}
        )
        campaign_40_50 = self.create_campaign(
            self.advertiser_2, targeting={"age_from": 40, "age_to": 50}
        )

        self.assertEqual(
            self.get_ad_response(self.female_client).data["ad_id"],
            campaign_40_50["campaign_id"],
        )
        self.assertEqual(
            self.get_ad_response(self.male_client).data["ad_id"],
            campaign_20_30["campaign_id"],
        )
        Campaign.objects.all().delete()

        campaign_all = self.create_campaign(
            self.advertiser_2, targeting={"age_from": 25, "age_to": 40}
        )
        self.assertEqual(
            self.get_ad_response(self.female_client).data["ad_id"],
            campaign_all["campaign_id"],
        )
        self.assertEqual(
            self.get_ad_response(self.male_client).data["ad_id"],
            campaign_all["campaign_id"],
        )

    def test_location_targeting(self):
        self.create_campaign(self.advertiser_1, targeting={"location": "New mexico"})
        self.assertEqual(self.get_ad_response(self.male_client).status_code, 200)
        self.assertEqual(self.get_ad_response(self.female_client).status_code, 404)

    def test_location_registry_targeting(self):
        self.create_campaign(self.advertiser_1, targeting={"location": "new mexico"})
        self.assertEqual(self.get_ad_response(self.male_client).status_code, 404)

    def test_complex_targeting_all_not(self):
        self.create_campaign(
            self.advertiser_1, targeting={"location": "Syberia", "age_to": 25}
        )
        self.assertEqual(self.get_ad_response(self.male_client).status_code, 404)
        self.assertEqual(self.get_ad_response(self.female_client).status_code, 404)
        self.assertEqual(self.get_ad_response(self.third_client).status_code, 404)

    def test_complex_targeting_simple(self):
        self.create_campaign(
            self.advertiser_2, targeting={"age_to": 45, "location": "Syberia"}
        )
        self.assertEqual(self.get_ad_response(self.third_client).status_code, 200)
        self.assertEqual(self.get_ad_response(self.female_client).status_code, 200)
        self.assertEqual(self.get_ad_response(self.male_client).status_code, 404)

    def test_complex_targeting_many(self):
        self.create_campaign(
            self.advertiser_1,
            targeting={
                "age_from": 20,
                "age_to": 42,
                "location": "Syberia",
                "gender": "MALE",
            },
        )
        self.create_campaign(
            self.advertiser_2,
            targeting={"age_from": 30, "age_to": 42, "gender": "MALE"},
        )
        campaign1 = self.create_campaign(
            self.advertiser_2,
            targeting={"age_from": 1, "location": "New mexico", "gender": "ALL"},
        )
        campaign2 = self.create_campaign(
            self.advertiser_2,
            targeting={
                "age_to": 40,
                "age_from": 1,
                "location": "Syberia",
                "gender": "ALL",
            },
        )
        self.create_campaign(
            self.advertiser_1, targeting={"age_from": 20, "location": "Moscow"}
        )
        self.create_campaign(
            self.advertiser_1, targeting={"age_to": 30, "gender": "FEMALE"}
        )
        campaign3 = self.create_campaign(
            self.advertiser_1,
            targeting={"age_from": 41, "location": "Syberia", "gender": "MALE"},
        )
        self.create_campaign(
            self.advertiser_2, targeting={"age_from": 42, "gender": "FEMALE"}
        )
        self.create_campaign(self.advertiser_1, targeting={"age_to": 46})
        self.assertEqual(
            campaign3["campaign_id"],
            self.get_ad_response(self.third_client).data["ad_id"],
        )
        self.assertEqual(
            campaign1["campaign_id"],
            self.get_ad_response(self.male_client).data["ad_id"],
        )
        self.assertEqual(
            campaign2["campaign_id"],
            self.get_ad_response(self.female_client).data["ad_id"],
        )

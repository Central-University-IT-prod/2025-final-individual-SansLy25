import uuid

from rest_framework.test import APITestCase
from rest_framework import status
from advertisers.models import Advertiser


class TestCreateUpdateAdvertiser(APITestCase):
    def setUp(self):
        self.incorrect_advertisers = [
            {},
            {"advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
            {"name": "string"},
            {"advertiser_id": "12312sd123", "name": "string"},
        ]

        self.correct_advertiser_1 = {
            "advertiser_id": str(uuid.uuid4()),
            "name": "bob",
        }
        self.updated_advertiser_1 = {
            "advertiser_id": self.correct_advertiser_1["advertiser_id"],
            "name": "clara",
        }

        self.correct_advertiser_2 = {
            "advertiser_id": str(uuid.uuid4()),
            "name": "jack",
        }

        self.correct_advertiser_3 = {
            "advertiser_id": str(uuid.uuid4()),
            "name": "dillan",
        }

        self.bulk_url = "/advertisers/bulk"
        self.advertiser_url = "/advertisers/"

    def test_invalid_create(self):
        for incorrect_advertiser in self.incorrect_advertisers:
            with self.subTest(incorrect_advertiser=incorrect_advertiser):
                response = self.client.post(
                    self.bulk_url, data=[incorrect_advertiser], format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_simple_create(self):
        data = [
            self.correct_advertiser_1,
            self.correct_advertiser_2,
            self.correct_advertiser_3,
        ]
        response = self.client.post(self.bulk_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)

    def test_db_save_and_id_overlap(self):
        data = [self.correct_advertiser_3]
        response = self.client.post(self.bulk_url, data=data, format="json")

        try:
            advertiser = Advertiser.objects.get(pk=response.data[0]["advertiser_id"])
            self.assertEqual(
                str(advertiser.id), self.correct_advertiser_3["advertiser_id"]
            )
        except Advertiser.DoesNotExist:
            self.fail("Advertiser does not created")

    def test_update_simple_object(self):
        data = [self.correct_advertiser_1, self.updated_advertiser_1]
        response = self.client.post(self.bulk_url, data=data, format="json")
        self.assertEqual(response.data, [self.updated_advertiser_1])
        self.assertEqual(Advertiser.objects.count(), 1)

    def test_create_update_many_objects(self):
        data = [
            self.correct_advertiser_1,
            self.correct_advertiser_2,
            self.updated_advertiser_1,
            self.correct_advertiser_3,
        ]

        response = self.client.post(self.bulk_url, data=data, format="json")
        self.assertEqual(
            response.data,
            [
                self.correct_advertiser_2,
                self.updated_advertiser_1,
                self.correct_advertiser_3,
            ],
        )
        self.assertEqual(Advertiser.objects.count(), 3)

    def test_create_update_count_simple_object(self):
        data1 = [self.correct_advertiser_1]
        data2 = [self.updated_advertiser_1, self.correct_advertiser_3]
        self.client.post(self.bulk_url, data=data1, format="json")
        self.client.post(self.bulk_url, data=data2, format="json")
        self.assertEqual(Advertiser.objects.count(), 2)

    def test_create_many_valid_one_invalid_object(self):
        data = [
            self.correct_advertiser_1,
            self.correct_advertiser_2,
            self.updated_advertiser_1,
            self.incorrect_advertisers[2],
            self.correct_advertiser_3,
        ]
        response = self.client.post(self.bulk_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_advertisers(self):
        data = [self.correct_advertiser_1]
        response_create = self.client.post(self.bulk_url, data=data, format="json")
        advertiser_id = response_create.data[0]["advertiser_id"]
        response = self.client.get(self.advertiser_url + advertiser_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data[0])

    def test_get_not_exist_advertiser(self):
        response = self.client.get(
            self.advertiser_url + "00000000-0000-0000-0000-000000000000", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

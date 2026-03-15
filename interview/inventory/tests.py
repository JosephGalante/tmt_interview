from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from interview.inventory.models import (
    Inventory,
    InventoryLanguage,
    InventoryTag,
    InventoryType,
)


class InventoryListCreateViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("inventory-list")
        self.inventory_type = InventoryType.objects.create(name="Movie")
        self.inventory_language = InventoryLanguage.objects.create(name="English")
        self.inventory_tag = InventoryTag.objects.create(name="Drama")

    def create_inventory(self, name: str, created_at: datetime) -> Inventory:
        inventory = Inventory.objects.create(
            name=name,
            type=self.inventory_type,
            language=self.inventory_language,
            metadata={"rating": "PG"},
        )
        inventory.tags.add(self.inventory_tag)
        Inventory.objects.filter(pk=inventory.pk).update(
            created_at=timezone.make_aware(created_at)
        )
        inventory.refresh_from_db()
        return inventory

    def test_get_returns_all_inventory_when_created_after_is_not_provided(self):
        first_inventory = self.create_inventory(
            "Older Item", datetime(2024, 1, 1, 10, 0)
        )
        second_inventory = self.create_inventory(
            "Newer Item", datetime(2024, 2, 1, 10, 0)
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [item["id"] for item in response.json()],
            [first_inventory.id, second_inventory.id],
        )

    def test_get_returns_empty_list_when_no_inventory_exists(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_get_filters_inventory_created_after_given_date(self):
        self.create_inventory("Older Item", datetime(2024, 1, 1, 10, 0))
        first_matching_inventory = self.create_inventory(
            "First Matching Item", datetime(2024, 2, 1, 10, 0)
        )
        second_matching_inventory = self.create_inventory(
            "Second Matching Item", datetime(2024, 2, 2, 10, 0)
        )

        response = self.client.get(self.url, {"created_after": "2024-01-15"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [first_matching_inventory.id, second_matching_inventory.id],
        )

    def test_get_returns_bad_request_for_invalid_created_after_date(self):
        response = self.client.get(self.url, {"created_after": "01-15-2024"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"error": "created_after must be a valid date in YYYY-MM-DD format."},
        )

    def test_get_excludes_inventory_created_on_boundary_date(self):
        self.create_inventory("Boundary Item", datetime(2024, 1, 15, 9, 0))
        matching_inventory = self.create_inventory(
            "After Boundary Item", datetime(2024, 1, 16, 9, 0)
        )

        response = self.client.get(self.url, {"created_after": "2024-01-15"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], matching_inventory.id)

    def test_get_returns_empty_list_for_future_created_after_date(self):
        self.create_inventory("Existing Item", datetime(2024, 1, 1, 10, 0))

        response = self.client.get(self.url, {"created_after": "2999-01-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_get_treats_empty_created_after_as_unfiltered(self):
        first_inventory = self.create_inventory(
            "Older Item", datetime(2024, 1, 1, 10, 0)
        )
        second_inventory = self.create_inventory(
            "Newer Item", datetime(2024, 2, 1, 10, 0)
        )

        response = self.client.get(self.url, {"created_after": ""})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [item["id"] for item in response.json()],
            [first_inventory.id, second_inventory.id],
        )

    def test_get_returns_inventory_in_created_at_order(self):
        newest_inventory = self.create_inventory(
            "Newest Item", datetime(2024, 3, 1, 10, 0)
        )
        oldest_inventory = self.create_inventory(
            "Oldest Item", datetime(2024, 1, 1, 10, 0)
        )
        middle_inventory = self.create_inventory(
            "Middle Item", datetime(2024, 2, 1, 10, 0)
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [oldest_inventory.id, middle_inventory.id, newest_inventory.id],
        )

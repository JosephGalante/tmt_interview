from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from interview.inventory.models import (
    Inventory,
    InventoryLanguage,
    InventoryTag,
    InventoryType,
)
from interview.order.models import Order


def create_inventory(name="Inventory Item"):
    inventory_type = InventoryType.objects.create(name="Movie")
    inventory_language = InventoryLanguage.objects.create(name="English")
    inventory_tag = InventoryTag.objects.create(name="Drama")

    inventory = Inventory.objects.create(
        name=name,
        type=inventory_type,
        language=inventory_language,
        metadata={"rating": "PG"},
    )
    inventory.tags.add(inventory_tag)

    return inventory


class OrderListCreateViewTests(APITestCase):
    def setUp(self):
        inventory = create_inventory()

        self.url = reverse("order-list")
        self.early_order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 1),
            embargo_date=date(2024, 1, 10),
            is_active=True,
        )
        self.matching_order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 5),
            embargo_date=date(2024, 1, 15),
            is_active=True,
        )
        self.late_order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 2, 1),
            embargo_date=date(2024, 2, 10),
            is_active=True,
        )

    def test_get_returns_all_orders_without_date_filters(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [self.early_order.id, self.matching_order.id, self.late_order.id],
        )

    def test_get_filters_orders_between_start_and_embargo_dates(self):
        response = self.client.get(
            self.url,
            {"start_date": "2024-01-02", "embargo_date": "2024-01-31"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()], [self.matching_order.id]
        )

    def test_get_returns_bad_request_when_only_one_date_is_provided(self):
        response = self.client.get(self.url, {"start_date": "2024-01-02"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"error": "start_date and embargo_date are both required."},
        )

    def test_get_returns_bad_request_for_invalid_date_format(self):
        response = self.client.get(
            self.url,
            {"start_date": "01-02-2024", "embargo_date": "2024-01-31"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "error": "start_date and embargo_date must be valid dates in YYYY-MM-DD format."
            },
        )

    def test_get_returns_bad_request_when_start_date_is_after_embargo_date(self):
        response = self.client.get(
            self.url,
            {"start_date": "2024-02-01", "embargo_date": "2024-01-31"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"error": "start_date must be on or before embargo_date."},
        )

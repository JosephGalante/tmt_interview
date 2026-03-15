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
from interview.order.models import Order, OrderTag


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


class OrderTagListViewTests(APITestCase):
    def setUp(self):
        inventory = create_inventory()
        self.order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 1),
            embargo_date=date(2024, 1, 15),
            is_active=True,
        )
        self.url = reverse("order-tags", kwargs={"id": self.order.id})

    def test_get_returns_tags_for_order(self):
        first_tag = OrderTag.objects.create(name="First Tag")
        second_tag = OrderTag.objects.create(name="Second Tag")
        self.order.tags.add(first_tag, second_tag)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [first_tag.id, second_tag.id],
        )

    def test_get_returns_empty_list_when_order_has_no_tags(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_get_returns_not_found_for_missing_order(self):
        response = self.client.get(
            reverse("order-tags", kwargs={"id": self.order.id + 1})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

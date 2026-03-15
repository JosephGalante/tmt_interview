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


class OrdersOnTagViewTests(APITestCase):
    def setUp(self):
        inventory = create_inventory()
        self.first_order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 1),
            embargo_date=date(2024, 1, 10),
            is_active=True,
        )
        self.second_order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 15),
            embargo_date=date(2024, 1, 25),
            is_active=True,
        )
        self.unrelated_order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 2, 1),
            embargo_date=date(2024, 2, 10),
            is_active=True,
        )
        self.tag = OrderTag.objects.create(name="Featured")
        self.first_order.tags.add(self.tag)
        self.second_order.tags.add(self.tag)
        self.url = reverse("tag-orders", kwargs={"id": self.tag.id})

    def test_get_returns_orders_for_tag(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.json()],
            [self.first_order.id, self.second_order.id],
        )

    def test_get_returns_empty_list_when_tag_has_no_orders(self):
        empty_tag = OrderTag.objects.create(name="Empty Tag")

        response = self.client.get(reverse("tag-orders", kwargs={"id": empty_tag.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_get_returns_not_found_for_missing_tag(self):
        response = self.client.get(
            reverse("tag-orders", kwargs={"id": self.tag.id + 1})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

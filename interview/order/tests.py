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


class DeactivateOrderViewTests(APITestCase):
    def setUp(self):
        inventory = create_inventory()

        self.order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 1),
            embargo_date=date(2024, 1, 15),
            is_active=True,
        )
        self.url = reverse("order-deactivate", kwargs={"id": self.order.id})

    def test_patch_deactivates_order(self):
        self.assertTrue(self.order.is_active)

        response = self.client.patch(self.url)

        self.order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.order.is_active)
        self.assertEqual(response.json()["id"], self.order.id)
        self.assertFalse(response.json()["is_active"])

    def test_patch_returns_not_found_for_missing_order(self):
        response = self.client.patch(
            reverse("order-deactivate", kwargs={"id": self.order.id + 1})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_keeps_order_inactive_when_already_deactivated(self):
        self.order.is_active = False
        self.order.save(update_fields=["is_active"])

        response = self.client.patch(self.url)

        self.order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.order.is_active)
        self.assertFalse(response.json()["is_active"])


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

   

from datetime import date

from django.urls import reverse
from rest_framework.test import APITestCase

from interview.inventory.models import (
    Inventory,
    InventoryLanguage,
    InventoryTag,
    InventoryType,
)
from interview.order.models import Order


class DeactivateOrderViewTests(APITestCase):
    def setUp(self):
        inventory_type = InventoryType.objects.create(name="Movie")
        inventory_language = InventoryLanguage.objects.create(name="English")
        inventory_tag = InventoryTag.objects.create(name="Drama")

        inventory = Inventory.objects.create(
            name="Inventory Item",
            type=inventory_type,
            language=inventory_language,
            metadata={"rating": "PG"},
        )
        inventory.tags.add(inventory_tag)

        self.order = Order.objects.create(
            inventory=inventory,
            start_date=date(2024, 1, 1),
            embargo_date=date(2024, 1, 15),
            is_active=True,
        )
        self.url = reverse("order-deactivate", kwargs={"id": self.order.id})

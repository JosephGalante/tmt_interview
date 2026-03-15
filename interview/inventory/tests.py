from datetime import datetime

from django.urls import reverse
from django.utils import timezone
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

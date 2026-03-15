from interview.inventory.models import (
    Inventory,
    InventoryLanguage,
    InventoryTag,
    InventoryType,
)


def create_inventory(
    name="Inventory Item",
    metadata=None,
    inventory_type=None,
    inventory_language=None,
    inventory_tag=None,
    type_name="Movie",
    language_name="English",
    tag_name="Drama",
):
    inventory_type = inventory_type or InventoryType.objects.create(name=type_name)
    inventory_language = inventory_language or InventoryLanguage.objects.create(
        name=language_name
    )
    inventory_tag = inventory_tag or InventoryTag.objects.create(name=tag_name)

    inventory = Inventory.objects.create(
        name=name,
        type=inventory_type,
        language=inventory_language,
        metadata=metadata or {"rating": "PG"},
    )
    inventory.tags.add(inventory_tag)

    return inventory


def create_inventory_dependencies(
    type_name="Movie", language_name="English", tag_name="Drama"
):
    return (
        InventoryType.objects.create(name=type_name),
        InventoryLanguage.objects.create(name=language_name),
        InventoryTag.objects.create(name=tag_name),
    )

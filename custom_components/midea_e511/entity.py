"""Base entity for the Midea E511 rice cooker integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CATEGORY, DOMAIN, MODEL
from .coordinator import E511Coordinator


class E511Entity(CoordinatorEntity[E511Coordinator]):
    """Base class for E511 entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: E511Coordinator,
        device_id: int,
        entity_key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._entity_key = entity_key
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{entity_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(device_id))},
            name=coordinator.device_name,
            manufacturer="Midea",
            model=MODEL,
            serial_number=coordinator.serial_number or None,
            suggested_area=CATEGORY,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.device.available

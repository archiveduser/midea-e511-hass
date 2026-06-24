"""Number entities for the Midea E511 rice cooker integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import E511Coordinator
from .entity import E511Entity


NUMBERS = (
    {
        "key": "order_time_hour",
        "name": "Schedule hour",
        "min": 0,
        "max": 24,
        "step": 1,
    },
    {
        "key": "order_time_min",
        "name": "Schedule minute",
        "min": 0,
        "max": 59,
        "step": 1,
    },
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up E511 number entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: E511Coordinator = entry_data["coordinator"]
    device_id: int = entry_data["device_id"]

    async_add_entities(
        [E511Number(coordinator, device_id, description) for description in NUMBERS]
    )


class E511Number(E511Entity, NumberEntity):
    """Number entity for schedule values."""

    def __init__(
        self,
        coordinator: E511Coordinator,
        device_id: int,
        description: dict[str, Any],
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            f"number_{description['key']}",
            description["name"],
        )
        self._key = description["key"]
        self._attr_native_min_value = description["min"]
        self._attr_native_max_value = description["max"]
        self._attr_native_step = description["step"]
        self._attr_mode = "box"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get(self._key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_control(self._key, int(value))

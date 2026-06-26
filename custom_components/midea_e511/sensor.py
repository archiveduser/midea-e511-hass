"""Sensor entities for the Midea E511 rice cooker integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_OPTIONS
from .coordinator import E511Coordinator
from .entity import E511Entity


SENSORS: tuple[dict[str, Any], ...] = (
    {
        "key": "work_status",
        "name": "Work status",
        "device_class": SensorDeviceClass.ENUM,
        "options": ["cancel", "schedule", "cooking", "keep_warm", "awakening_rice"],
    },
    {
        "key": "mode",
        "name": "Mode",
        "device_class": SensorDeviceClass.ENUM,
        "options": list(MODE_OPTIONS.values()),
    },
    {
        "key": "remain_time",
        "name": "Remaining time",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.MINUTES,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "warming_time",
        "name": "Warming time",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.MINUTES,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "bottom_temperature",
        "name": "Bottom temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "top_temperature",
        "name": "Top temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "error_code",
        "name": "Error code",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "work_stage",
        "name": "Work stage",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up E511 sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: E511Coordinator = entry_data["coordinator"]
    device_id: int = entry_data["device_id"]

    entities: list[SensorEntity] = [
        E511Sensor(coordinator, device_id, description) for description in SENSORS
    ]
    async_add_entities(entities)


class E511Sensor(E511Entity, SensorEntity):
    """A sensor backed by a cooker status attribute."""

    def __init__(
        self,
        coordinator: E511Coordinator,
        device_id: int,
        description: dict[str, Any],
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            f"sensor_{description['key']}",
            description["name"],
        )
        self._key = description["key"]
        self._attr_device_class = description.get("device_class")
        self._attr_native_unit_of_measurement = description.get("unit")
        self._attr_state_class = description.get("state_class")
        self._attr_entity_category = description.get("entity_category")
        if description.get("options"):
            self._attr_options = description["options"]

    @property
    def native_value(self) -> Any:
        if not self.available:
            return None

        data = self.coordinator.data or {}
        if self._key == "remain_time":
            return data.get("remain_time", _minutes(data, "left_time"))
        if self._key == "warming_time":
            return data.get("warming_time", _minutes(data, "warm_time"))

        value = data.get(self._key)
        if value == "":
            return None
        return value


def _minutes(data: dict[str, Any], prefix: str) -> int | None:
    hour = data.get(f"{prefix}_hour")
    minute = data.get(f"{prefix}_min")
    if hour is None or minute is None:
        return None
    try:
        return int(hour) * 60 + int(minute)
    except (TypeError, ValueError):
        return None

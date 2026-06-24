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
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
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
        "key": "top_temperature",
        "name": "Top temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
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
        "key": "indoor_temperature",
        "name": "Indoor temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "voltage",
        "name": "Voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": UnitOfElectricPotential.VOLT,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {"key": "error_code", "name": "Error code"},
    {"key": "work_stage", "name": "Work stage"},
    {"key": "work_flag", "name": "Work flag"},
    {"key": "rice_level", "name": "Rice level"},
    {
        "key": "pressure_state",
        "name": "Pressure state",
        "device_class": SensorDeviceClass.ENUM,
        "options": ["inexistence", "existence"],
    },
    {"key": "control_src", "name": "Control source"},
    {"key": "cmd_code", "name": "Command code"},
    {"key": "cuisine_end", "name": "Cuisine end"},
    {"key": "show_time", "name": "Show time"},
    {"key": "dry_braised", "name": "Dry braised"},
    {"key": "mat_rice", "name": "Mat rice"},
    {"key": "hot_cuisine", "name": "Hot cuisine"},
    {"key": "flank_hot", "name": "Flank hot"},
    {"key": "top_hot", "name": "Top heating"},
    {"key": "bottom_hot", "name": "Bottom heating"},
    {"key": "step_expect_time", "name": "Step expected time"},
    {"key": "step_actual_time", "name": "Step actual time"},
    {"key": "init_order_time_hour", "name": "Initial order hour"},
    {"key": "init_order_time_min", "name": "Initial order minute"},
    {"key": "init_work_time_hour", "name": "Initial work hour"},
    {"key": "init_work_time_min", "name": "Initial work minute"},
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
    entities.append(E511LanIpSensor(coordinator, device_id))
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


class E511LanIpSensor(E511Entity, SensorEntity):
    """Diagnostic sensor exposing the configured LAN IP."""

    def __init__(self, coordinator: E511Coordinator, device_id: int) -> None:
        super().__init__(coordinator, device_id, "sensor_lan_ip", "LAN IP")

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self) -> str:
        return self.coordinator.device.controller.ip


def _minutes(data: dict[str, Any], prefix: str) -> int | None:
    hour = data.get(f"{prefix}_hour")
    minute = data.get(f"{prefix}_min")
    if hour is None or minute is None:
        return None
    try:
        return int(hour) * 60 + int(minute)
    except (TypeError, ValueError):
        return None

"""Select entities for the Midea E511 rice cooker integration."""

from __future__ import annotations

import asyncio

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_OPTIONS
from .coordinator import E511Coordinator
from .entity import E511Entity


SELECTS = (
    ("mode", "模式", MODE_OPTIONS),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up E511 selects."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: E511Coordinator = entry_data["coordinator"]
    device_id: int = entry_data["device_id"]

    async_add_entities(
        [
            E511Select(coordinator, device_id, key, name, options)
            for key, name, options in SELECTS
        ]
    )


class E511Select(E511Entity, SelectEntity):
    """Select entity for a writable cooker attribute."""

    def __init__(
        self,
        coordinator: E511Coordinator,
        device_id: int,
        key: str,
        name: str,
        options: dict[str, str],
    ) -> None:
        super().__init__(coordinator, device_id, f"select_{key}", name)
        self._key = key
        self._options_map = options
        self._attr_options = list(options)

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data or {}
        value = data.get(self._key)
        for label, protocol_value in self._options_map.items():
            if value == protocol_value:
                return label
        return None

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            return

        data = self.coordinator.data or {}
        mode = self._options_map[option]

        if data.get("work_status") != "cancel":
            await self.coordinator.async_set_control({"work_status": "cancel"})
            await asyncio.sleep(1)
            await self.coordinator.async_refresh_device()

        await self.coordinator.async_set_control(
            {
                "mode": mode,
                "work_status": "cancel",
            }
        )
        await asyncio.sleep(1)
        await self.coordinator.async_refresh_device()

"""Select entities for the Midea E511 rice cooker integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_OPTIONS, MOUTHFEEL_OPTIONS, RICE_TYPE_OPTIONS
from .coordinator import E511Coordinator
from .entity import E511Entity


SELECTS = (
    ("mode", "Mode", MODE_OPTIONS),
    ("mouthfeel", "Mouthfeel", MOUTHFEEL_OPTIONS),
    ("rice_type", "Rice type", RICE_TYPE_OPTIONS),
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
            E511Select(coordinator, device_id, key, name, list(options))
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
        options: list[str],
    ) -> None:
        super().__init__(coordinator, device_id, f"select_{key}", name)
        self._key = key
        self._attr_options = options

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data or {}
        value = data.get(self._key)
        if isinstance(value, str) and value in self.options:
            return value
        if isinstance(value, int) and 0 <= value < len(self.options):
            return self.options[value]
        return None

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            return
        await self.coordinator.async_set_control(self._key, option)

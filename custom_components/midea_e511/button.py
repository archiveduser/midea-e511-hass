"""Button entities for the Midea E511 rice cooker integration."""

from __future__ import annotations

import asyncio

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, build_start_command
from .coordinator import E511Coordinator
from .entity import E511Entity


BUTTONS = (
    ("start", "开始", None),
    ("cancel", "取消", {"work_status": "cancel"}),
    ("keep_warm", "保温", {"work_status": "keep_warm"}),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up E511 buttons."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: E511Coordinator = entry_data["coordinator"]
    device_id: int = entry_data["device_id"]

    async_add_entities(
        [
            E511Button(coordinator, device_id, key, name, command)
            for key, name, command in BUTTONS
        ]
    )


class E511Button(E511Entity, ButtonEntity):
    """Button entity for E511 commands."""

    def __init__(
        self,
        coordinator: E511Coordinator,
        device_id: int,
        key: str,
        name: str,
        command: dict[str, str] | None,
    ) -> None:
        super().__init__(coordinator, device_id, f"button_{key}", name)
        self._command = command

    async def async_press(self) -> None:
        if self._command is None:
            data = self.coordinator.data or {}
            if data.get("work_status") != "cancel":
                await self.coordinator.async_set_control({"work_status": "cancel"})
                await asyncio.sleep(1)
                await self.coordinator.async_refresh_device()
                data = self.coordinator.data or {}
            command = build_start_command(data.get("mode"), data)
        else:
            command = self._command

        await self.coordinator.async_set_control(command)
        await asyncio.sleep(1)
        await self.coordinator.async_refresh_device()

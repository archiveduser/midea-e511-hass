"""Button entities for the Midea E511 rice cooker integration."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_MODE, DOMAIN
from .coordinator import E511Coordinator
from .entity import E511Entity


BUTTONS = (
    ("start", "Start", {"work_status": "cooking"}),
    ("cancel", "Cancel", {"work_status": "cancel"}),
    ("keep_warm", "Keep warm", {"work_status": "keep_warm"}),
    ("schedule", "Schedule", {"work_status": "schedule"}),
    ("refresh", "Refresh", None),
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
        command: dict[str, Any] | None,
    ) -> None:
        super().__init__(coordinator, device_id, f"button_{key}", name)
        self._key = key
        self._command = command

    async def async_press(self) -> None:
        if self._key == "refresh":
            await self.coordinator.async_refresh_device()
            return

        command = self._build_command()
        await self.coordinator.async_set_control(command)
        await asyncio.sleep(1)
        await self.coordinator.async_refresh_device()

    def _build_command(self) -> dict[str, Any]:
        command = deepcopy(self._command) if self._command else {}
        data = self.coordinator.data or {}

        if self._key in {"start", "schedule"}:
            command.setdefault("mode", data.get("mode") or DEFAULT_MODE)

        if self._key == "schedule":
            command.setdefault("order_time_hour", int(data.get("order_time_hour") or 0))
            command.setdefault("order_time_min", int(data.get("order_time_min") or 0))

        if self._key == "start":
            for attr in (
                "mouthfeel",
                "rice_type",
                "rice_level",
                "left_time_hour",
                "left_time_min",
                "order_time_hour",
                "order_time_min",
            ):
                if attr in data:
                    command.setdefault(attr, data[attr])

        return command

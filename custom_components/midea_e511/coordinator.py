"""Coordinator for the Midea E511 rice cooker integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import build_start_command
from .midea_lib.device import MideaDevice

_LOGGER = logging.getLogger(__name__)

ControlValue = str | int | float | bool | None


class E511Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Bridge callbacks from the synchronous Midea device into Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: MideaDevice,
        device_name: str,
        serial_number: str = "",
    ) -> None:
        self.device = device
        self.device_name = device_name
        self.serial_number = serial_number
        self._active = True

        super().__init__(
            hass,
            _LOGGER,
            name=f"Midea E511 {device_name}",
            update_interval=None,
        )

        device.register_update(self._device_update_callback)

    def deactivate(self) -> None:
        """Stop processing callbacks after unload."""
        self._active = False

    def _device_update_callback(self) -> None:
        if not self._active or self.hass.is_stopping:
            return

        self.hass.loop.call_soon_threadsafe(
            self.async_set_updated_data, dict(self.device.data)
        )

    async def _async_update_data(self) -> dict[str, Any]:
        return dict(self.device.data)

    async def async_set_control(
        self,
        attr: str | dict[str, ControlValue],
        value: ControlValue = None,
    ) -> dict[str, Any]:
        """Send one or more controls to the cooker."""
        if isinstance(attr, dict):
            await self.hass.async_add_executor_job(self.device.set_attributes, attr)
        else:
            await self.hass.async_add_executor_job(self.device.set_attribute, attr, value)
        return dict(self.device.data)

    async def async_refresh_device(self) -> None:
        """Ask the device for fresh status."""
        await self.hass.async_add_executor_job(self.device.refresh_status)

    async def async_start_mode(self, mode: str | None) -> dict[str, Any]:
        """Start a cooker mode, cancelling the current run first when needed."""
        data = self.data or {}
        if data.get("work_status") != "cancel":
            await self.async_set_control({"work_status": "cancel"})
            await asyncio.sleep(1)
            await self.async_refresh_device()
            data = self.data or {}

        command = build_start_command(mode, data)
        result = await self.async_set_control(command)
        await asyncio.sleep(1)
        await self.async_refresh_device()
        return result

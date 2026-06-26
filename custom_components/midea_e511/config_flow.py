"""Config flow for the Midea E511 rice cooker integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_IP,
    CONF_KEY,
    CONF_PORT,
    CONF_SN,
    CONF_SN8,
    CONF_TOKEN,
    DEFAULT_DEVICE_ID,
    DEFAULT_PORT,
    DEFAULT_SN,
    DOMAIN,
    SN8,
    device_name_from_sn,
    sn8_from_sn,
)
from .discovery import discover_device

_LOGGER = logging.getLogger(__name__)


def _validate_hex(value: str) -> bool:
    if not value:
        return False
    try:
        bytes.fromhex(value)
    except ValueError:
        return False
    return True


class MideaEAE511ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for a manually configured E511 rice cooker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            data = dict(user_input)
            data[CONF_TOKEN] = data[CONF_TOKEN].strip()
            data[CONF_KEY] = data[CONF_KEY].strip()
            data[CONF_IP] = data[CONF_IP].strip()

            if not _validate_hex(data[CONF_TOKEN]):
                errors[CONF_TOKEN] = "invalid_hex"
            if not _validate_hex(data[CONF_KEY]):
                errors[CONF_KEY] = "invalid_hex"

            if not errors:
                discovery_info: dict[str, Any] = {}
                try:
                    discovery_info = await self.hass.async_add_executor_job(
                        discover_device, data[CONF_IP]
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to discover MB-FB50E511 metadata from %s: %s",
                        data[CONF_IP],
                        err,
                    )

                sn = discovery_info.get(CONF_SN) or DEFAULT_SN
                device_id = discovery_info.get(CONF_DEVICE_ID) or DEFAULT_DEVICE_ID
                sn8 = discovery_info.get(CONF_SN8) or sn8_from_sn(sn) or SN8
                device_name = device_name_from_sn(sn)

                data[CONF_PORT] = DEFAULT_PORT
                data[CONF_DEVICE_ID] = device_id
                data[CONF_SN] = sn
                data[CONF_SN8] = sn8
                data[CONF_DEVICE_NAME] = device_name

                await self.async_set_unique_id(f"{DOMAIN}_{data[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured(updates={CONF_IP: data[CONF_IP]})

                return self.async_create_entry(
                    title=device_name,
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP): str,
                    vol.Required(CONF_TOKEN): str,
                    vol.Required(CONF_KEY): str,
                }
            ),
            errors=errors,
        )

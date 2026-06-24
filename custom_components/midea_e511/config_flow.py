"""Config flow for the Midea E511 rice cooker integration."""

from __future__ import annotations

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
    CONF_TOKEN,
    DEFAULT_DEVICE_ID,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DOMAIN,
)


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
                await self.async_set_unique_id(f"{DOMAIN}_{data[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured(updates={CONF_IP: data[CONF_IP]})

                return self.async_create_entry(
                    title=data.get(CONF_DEVICE_NAME) or DEFAULT_DEVICE_NAME,
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP): str,
                    vol.Required(CONF_TOKEN): str,
                    vol.Required(CONF_KEY): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): int,
                    vol.Optional(
                        CONF_DEVICE_NAME, default=DEFAULT_DEVICE_NAME
                    ): str,
                }
            ),
            errors=errors,
        )

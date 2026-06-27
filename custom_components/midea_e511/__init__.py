"""Midea E511 rice cooker integration."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    ATTR_MODE,
    CALCULATE_CONFIG,
    CATEGORY,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_IP,
    CONF_KEY,
    CONF_PORT,
    CONF_SN,
    CONF_SN8,
    CONF_TOKEN,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DEFAULT_VALUES,
    DEVICE_TYPE,
    DOMAIN,
    KEEP_WARM_MODE,
    LUA_COMMON_PATH,
    LUA_DEVICE_FILE,
    MODE_OPTIONS,
    MODEL,
    PLATFORMS,
    PROTOCOL,
    SERVICE_START_MODE,
    SUBTYPE,
    display_sn,
    resolve_mode,
)
from .coordinator import E511Coordinator
from .midea_lib.device import MideaDevice
from .midea_lib.lua import ensure_lua_files, write_file

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
START_MODE_SCHEMA = vol.Schema({vol.Required(ATTR_MODE): cv.string})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up common Lua files used by the local protocol codec."""
    hass.data.setdefault(DOMAIN, {})

    lua_path = hass.config.path(LUA_COMMON_PATH)
    os.makedirs(lua_path, exist_ok=True)

    cjson, bit, cjson_lua, bit_lua = await hass.async_add_executor_job(
        ensure_lua_files, lua_path
    )

    for file_path, content in ((cjson, cjson_lua), (bit, bit_lua)):
        if not os.path.exists(file_path):
            await hass.async_add_executor_job(write_file, file_path, content)

    async def _async_handle_start_mode(call: ServiceCall) -> None:
        mode = resolve_mode(call.data[ATTR_MODE])
        if mode is None:
            raise HomeAssistantError(
                "Unsupported MB-FB50E511 mode. Use one of: "
                f"{', '.join([*MODE_OPTIONS, *MODE_OPTIONS.values(), KEEP_WARM_MODE])}"
            )

        coordinators = [
            entry_data["coordinator"]
            for entry_data in hass.data.get(DOMAIN, {}).values()
            if "coordinator" in entry_data
        ]
        if not coordinators:
            raise HomeAssistantError("No Midea MB-FB50E511 devices are configured")

        await asyncio.gather(
            *(coordinator.async_start_mode(mode) for coordinator in coordinators)
        )

    if not hass.services.has_service(DOMAIN, SERVICE_START_MODE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_START_MODE,
            _async_handle_start_mode,
            schema=START_MODE_SCHEMA,
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an E511 rice cooker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    device_id = entry.data[CONF_DEVICE_ID]
    device_name = entry.data.get(CONF_DEVICE_NAME) or DEFAULT_DEVICE_NAME
    sn = entry.data[CONF_SN]
    sn8 = entry.data[CONF_SN8]
    serial_number = display_sn(sn)
    lua_file = Path(__file__).parent / "lua" / LUA_DEVICE_FILE
    lua_common_dir = Path(hass.config.config_dir) / LUA_COMMON_PATH

    def _open_device() -> MideaDevice:
        device = MideaDevice(
            device_id=device_id,
            device_type=DEVICE_TYPE,
            ip_address=entry.data[CONF_IP],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            token=entry.data[CONF_TOKEN],
            key=entry.data[CONF_KEY],
            protocol=PROTOCOL,
            model=MODEL,
            subtype=SUBTYPE,
            sn=sn,
            sn8=sn8,
            lua_file=str(lua_file),
            lua_common_dir=str(lua_common_dir),
            device_name=device_name,
            calculate_config=CALCULATE_CONFIG,
            default_values=DEFAULT_VALUES,
            category=CATEGORY,
            enable_polling=False,
        )
        device.open()
        for _ in range(10):
            if device.available:
                break
            import time

            time.sleep(0.5)
        if device.available:
            device.refresh_status()
        return device

    try:
        device = await hass.async_add_executor_job(_open_device)
    except Exception as err:
        _LOGGER.error("Failed to initialize E511 rice cooker: %s", err)
        return False

    if not device.available:
        _LOGGER.warning(
            "E511 rice cooker did not connect during setup; background reconnect will continue"
        )

    coordinator = E511Coordinator(hass, device, device_name, serial_number)
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "device": device,
        "device_id": device_id,
    }

    if device.data:
        coordinator.async_set_updated_data(dict(device.data))
    else:
        await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an E511 rice cooker."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        entry_data = hass.data[DOMAIN].pop(entry.entry_id, {})
        coordinator = entry_data.get("coordinator")
        if coordinator:
            coordinator.deactivate()
        device = entry_data.get("device")
        if device:
            await hass.async_add_executor_job(device.close)
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)

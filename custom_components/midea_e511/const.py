"""Constants for the Midea E511 rice cooker integration."""

from homeassistant.const import Platform

DOMAIN = "midea_e511"

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_IP = "ip_address"
CONF_KEY = "key"
CONF_PORT = "port"
CONF_SN = "sn"
CONF_SN8 = "sn8"
CONF_TOKEN = "token"

DEFAULT_DEVICE_ID = 210006724010482
DEFAULT_DEVICE_NAME = "Midea MB-FB50E511"
DEFAULT_PORT = 6444
DEFAULT_MODE = "stewing"
DEFAULT_SN = "0000EA51161000579351011006508SP5"

DEVICE_TYPE = 0xEA
PROTOCOL = 3
SUBTYPE = 0

SN_PREFIX = "0000EA"
SN8 = "61000579"
MODEL = "MB-FB50Easy501/MB-FB50E511"
CATEGORY = "rice-cooker"

LUA_DEVICE_FILE = "T0xEA_61000579.lua"
LUA_COMMON_PATH = f".storage/{DOMAIN}/lua_common"

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BUTTON,
]

MODE_OPTIONS = {
    "香浓粥": "fragrant_dense_congee",
    "柴火饭": "firewood_rice",
    "快速饭": "fast_rice",
    "精华饭": "essence_rice",
    "寿司饭": "sushi_rice",
    "石锅饭": "stone_bowl_rice",
    "热饭": "heat_rice",
    "蒸煮": "stewing",
    "煲汤": "cook_soup",
    "煮粥": "boil_congee",
    "稀饭": "gruel",
}

MODE_START_DEFAULTS = {
    "fragrant_dense_congee": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 1,
        "left_time_min": 0,
    },
    "firewood_rice": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 40,
    },
    "fast_rice": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 30,
    },
    "essence_rice": {
        "mouthfeel": "middle",
        "rice_type": "longrain",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 58,
    },
    "sushi_rice": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 58,
    },
    "stone_bowl_rice": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 58,
    },
    "heat_rice": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 25,
    },
    "stewing": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 30,
    },
    "cook_soup": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 2,
        "left_time_min": 0,
    },
    "boil_congee": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 2,
        "left_time_min": 0,
    },
    "gruel": {
        "mouthfeel": "none",
        "rice_type": "none",
        "rice_level": 3,
        "left_time_hour": 0,
        "left_time_min": 58,
    },
}

CALCULATE_CONFIG = {
    "get": [
        {
            "lvalue": "[remain_time]",
            "rvalue": "[left_time_hour] * 60 + [left_time_min]",
        },
        {
            "lvalue": "[warming_time]",
            "rvalue": "[warm_time_hour] * 60 + [warm_time_min]",
        },
    ],
    "set": {},
}

DEFAULT_VALUES = {
    "mode": DEFAULT_MODE,
    "work_status": "cancel",
    "mouthfeel": "none",
    "rice_type": "none",
    "left_time_hour": 0,
    "left_time_min": 0,
    "warm_time_hour": 0,
    "warm_time_min": 0,
}


def display_sn(sn: str | None) -> str:
    """Return the user-facing serial number without the Midea type prefix."""
    if not sn:
        return ""
    if sn.startswith(SN_PREFIX):
        return sn[len(SN_PREFIX) :]
    return sn


def device_name_from_sn(sn: str | None) -> str:
    """Build the configured device name from the serial number suffix."""
    visible_sn = display_sn(sn)
    if not visible_sn:
        return DEFAULT_DEVICE_NAME
    return f"{DEFAULT_DEVICE_NAME}({visible_sn[-4:]})"


def sn8_from_sn(sn: str | None) -> str:
    """Extract the SN8 code used by the local Lua profile."""
    if not sn or len(sn) <= 17:
        return SN8
    return sn[9:17]


def build_start_command(mode: str | None, data: dict) -> dict:
    """Build a start command using mode defaults captured from the cooker."""
    if mode in (None, "", "cancel", "keep_warm"):
        mode = data.get("mode") or DEFAULT_MODE
    if mode in (None, "", "cancel", "keep_warm"):
        mode = DEFAULT_MODE

    command = {
        "mode": mode,
        "work_status": "cooking",
    }
    command.update(MODE_START_DEFAULTS.get(mode, {}))

    for attr in ("mouthfeel", "rice_type", "rice_level"):
        if attr not in command and attr in data:
            command[attr] = data[attr]

    return command

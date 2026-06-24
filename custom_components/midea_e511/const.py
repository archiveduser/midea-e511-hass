"""Constants for the Midea E511 rice cooker integration."""

from homeassistant.const import Platform

DOMAIN = "midea_e511"

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_IP = "ip_address"
CONF_KEY = "key"
CONF_PORT = "port"
CONF_TOKEN = "token"

DEFAULT_DEVICE_ID = 210006724010482
DEFAULT_DEVICE_NAME = "Midea MB-FB50E511"
DEFAULT_PORT = 6444
DEFAULT_MODE = "stewing"

DEVICE_TYPE = 0xEA
PROTOCOL = 3
SUBTYPE = 0

SN = "0000EA51161000579351011006508SP5"
SN8 = "61000579"
MODEL = "MB-FB50Easy501/MB-FB50E511"
CATEGORY = "rice-cooker"

LUA_DEVICE_FILE = "T0xEA_61000579.lua"
LUA_COMMON_PATH = f".storage/{DOMAIN}/lua_common"

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BUTTON,
    Platform.NUMBER,
]

MODE_OPTIONS = [
    "reserve",
    "cook_rice",
    "fast_cook_rice",
    "standard_cook_rice",
    "gruel",
    "cook_congee",
    "stew_soup",
    "stewing",
    "heat_rice",
    "make_cake",
    "yoghourt",
    "soup_rice",
    "coarse_rice",
    "five_ceeals_rice",
    "eight_treasures_rice",
    "crispy_rice",
    "shelled_rice",
    "eight_treasures_congee",
    "infant_congee",
    "older_rice",
    "rice_soup",
    "rice_paste",
    "egg_custard",
    "warm_milk",
    "hot_spring_egg",
    "millet_congee",
    "firewood_rice",
    "few_rice",
    "red_potato",
    "corn",
    "quick_freeze_bun",
    "steam_ribs",
    "steam_egg",
    "coarse_congee",
    "steep_rice",
    "appetizing_congee",
    "corn_congee",
    "sprout_rice",
    "luscious_rice",
    "luscious_boiled",
    "fast_rice",
    "fast_boil",
    "bean_rice_congee",
    "fast_congee",
    "baby_congee",
    "cook_soup",
    "congee_coup",
    "steam_corn",
    "steam_red_potato",
    "boil_congee",
    "delicious_steam",
    "boil_egg",
    "rice_wine",
    "fruit_vegetable_paste",
    "vegetable_porridge",
    "pork_porridge",
    "fragrant_rice",
    "assorte_rice",
    "steame_fish",
    "baby_rice",
    "essence_rice",
    "fragrant_dense_congee",
    "one_two_cook",
    "original_steame",
    "hot_fast_rice",
    "online_celebrity_rice",
    "sushi_rice",
    "stone_bowl_rice",
    "no_water_treat",
    "keep_fresh",
    "low_sugar_rice",
    "black_buckwheat_rice",
    "resveratrol_rice",
    "yellow_wheat_rice",
    "green_buckwheat_rice",
    "roughage_rice",
    "millet_mixed_rice",
    "iron_pan_rice",
    "olla_pan_rice",
    "vegetable_rice",
    "baby_side",
    "regimen_congee",
    "earthen_pot_congee",
    "regimen_soup",
    "pottery_jar_soup",
    "canton_soup",
    "nutrition_stew",
    "northeast_stew",
    "uncap_boil",
    "trichromatic_coarse_grain",
    "four_color_vegetables",
    "egg",
    "chop",
    "clean",
    "keep_warm",
    "diy",
    "smart",
]

MOUTHFEEL_OPTIONS = ["none", "soft", "middle", "hard"]
RICE_TYPE_OPTIONS = ["none", "northeast", "longrain", "fragrant", "five"]

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
    "order_time_hour": 0,
    "order_time_min": 0,
    "left_time_hour": 0,
    "left_time_min": 0,
    "warm_time_hour": 0,
    "warm_time_min": 0,
}

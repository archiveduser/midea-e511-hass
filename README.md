# Midea Rice Cooker(MB-FB50E511) for Home Assistant

Home Assistant custom integration for the Midea MB-FB50E511 rice cooker.

This integration is focused on local LAN control for the Midea MB-FB50E511
rice cooker. It does not use a Midea cloud account during setup. You manually
provide the cooker IP address, token, and key, then Home Assistant talks to the
device over the local Midea protocol.

## Features

- Manual Home Assistant UI setup
- Local protocol V3 connection
- Status sensors for work status, remaining time, warming time, temperatures,
  voltage, error code, work stage, and related cooker flags
- Mode select entity with a focused MB-FB50E511 mode list
- Buttons for cancel and keep warm

## Installation

### HACS Custom Repository

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add this repository:

   ```text
   https://github.com/archiveduser/midea-e511-hass
   ```

5. Select category **Integration**.
6. Install **Midea Rice Cooker(MB-FB50E511)**.
7. Restart Home Assistant.

### Manual Installation

Copy this directory into your Home Assistant config directory:

```text
custom_components/midea_e511
```

After copying, restart Home Assistant.

## Configuration

1. In Home Assistant, go to **Settings** -> **Devices & services**.
2. Click **Add integration**.
3. Search for **Midea Rice Cooker(MB-FB50E511)**.
4. Enter:
   - IP address
   - Token
   - Key
   - Port, usually `6444`
   - Device ID, optional unless your cooker uses a different ID
   - Device name

The token and key must be hexadecimal strings for the local Midea V3 protocol.

## Usage

After setup, the integration creates entities for the cooker.

To start or switch a cooking mode:

1. Choose a mode from the **模式** select entity.
2. The integration sends `cancel` first if the cooker is already running.
3. The integration then starts the selected mode with `work_status=cooking`.

Available mode labels are currently Chinese and mapped to temporary protocol
values:

- 香浓粥 -> `fragrant_dense_congee`
- 柴火饭 -> `firewood_rice`
- 快速饭 -> `fast_rice`
- 精华饭 -> `essence_rice`
- 寿司饭 -> `sushi_rice`
- 石锅饭 -> `stone_bowl_rice`
- 热饭 -> `heat_rice`
- 蒸煮 -> `stewing`
- 煲汤 -> `cook_soup`
- 煮粥 -> `cook_congee`
- 稀饭 -> `gruel`

To stop the cooker, press **Cancel**. To enter keep-warm mode, press
**Keep warm**.

## Notes

The MB-FB50E511 control path uses `work_status` commands for cooking, cancel,
and keep warm. This differs from some generic Midea rice cooker mappings that
use `work_switch`.

## Credits

This integration was developed with Codex.

Part of the local protocol, Lua runtime, encryption, packet handling, and device
communication code is based on
[Cyborg2017/midea_smart_home](https://github.com/Cyborg2017/midea_smart_home).

The E511-specific behavior and Home Assistant integration layout were adapted
for the MB-FB50E511 rice cooker.

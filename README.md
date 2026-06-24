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
- Select entities for cooking mode, mouthfeel, and rice type
- Number entities for scheduled hour and minute
- Buttons for start, cancel, keep warm, schedule, and refresh

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

To start cooking:

1. Choose a cooking mode from the **Mode** select entity.
2. Optionally choose **Mouthfeel** and **Rice type**.
3. Press the **Start** button.

To schedule cooking:

1. Choose a cooking mode.
2. Set **Schedule hour** and **Schedule minute**.
3. Press the **Schedule** button.

To stop the cooker, press **Cancel**. To enter keep-warm mode, press
**Keep warm**.

## Notes

The MB-FB50E511 control path uses `work_status` commands for start, cancel,
keep warm, and schedule. This differs from some generic Midea rice cooker
mappings that use `work_switch`.

## Credits

This integration was developed with Codex.

Part of the local protocol, Lua runtime, encryption, packet handling, and device
communication code is based on
[Cyborg2017/midea_smart_home](https://github.com/Cyborg2017/midea_smart_home).

The E511-specific behavior and Home Assistant integration layout were adapted
for the MB-FB50E511 rice cooker.

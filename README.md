# Teams → Govee status light

Drives a **Govee H6053** RGBIC light bar from your **Microsoft Teams presence**, entirely locally:

| Teams status | Light |
|---|---|
| Available | 🟢 green |
| Busy / Do Not Disturb / in a call | 🔴 red |
| Away / Be right back | 🟡 yellow |
| Offline | ⚫ off |

No IFTTT, no Govee cloud/LAN API, no Microsoft Graph — none of which work for this
model/tenant (see [Why this approach](#why-this-approach)). Instead it reads presence from
the local Teams logs and sends color commands over Bluetooth (BLE).

## How it works

- **`teams_presence.py`** — reads the newest new-Teams log under
  `%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\Logs`,
  parsing both `availability: X` lines and taskbar `status X` overlay lines
  (Do Not Disturb is *only* emitted as `status Do not disturb`).
- **`govee_light.py`** — BLE control. Writes 20-byte packets (19-byte payload + XOR
  checksum) to characteristic `00010203-0405-0607-0809-0a0b0c0d2b11`; color uses the
  segmented RGBIC command `33 05 15 01 RR GG BB ...`.
- **`main.py`** — polls every 5 s and updates the light only when the status changes.
- **`config.py`** — device address, colors, and the availability→color mapping.
- **`scan.py`** — setup helper: lists nearby BLE devices so you can find the light's
  address and put it in `config.py`.

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install bleak
.\.venv\Scripts\python.exe scan.py        # confirm the device address, update config.py
.\.venv\Scripts\python.exe main.py        # run
```

### Run automatically at login (Windows)

A scheduled task `TeamsGoveeLight` runs it hidden at logon via `pythonw`:

```powershell
Get-ScheduledTask -TaskName TeamsGoveeLight      # status
Stop-ScheduledTask -TaskName TeamsGoveeLight     # stop
Start-ScheduledTask -TaskName TeamsGoveeLight    # start
```

## Requirements & caveats

- An always-on PC within ~10 m Bluetooth range of the light.
- Teams must be running (presence comes from its logs; otherwise the light holds last color).
- Log parsing is inherently fragile — a Teams update could change the format and break
  presence detection. Check `runtime.log` if colors stop tracking.

## Why this approach

- **IFTTT**: the Webhooks "Receive a web request" trigger now requires paid Pro.
- **Govee Cloud Developer API**: H6053 is not on the supported-models list.
- **Govee LAN API**: H6053 is Bluetooth-only; no LAN control.
- **Microsoft Graph presence**: tenant has user consent disabled, so it needs IT admin
  approval. BLE + local logs avoids all of the above.

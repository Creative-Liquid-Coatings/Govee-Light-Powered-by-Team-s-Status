"""Configuration for the Teams-status Govee light."""

# --- Govee H6053 ---
DEVICE_ADDRESS = "D6:32:37:36:2C:43"   # from scan.py
BRIGHTNESS = 0xFF                       # 0x01..0xFF

# --- Polling ---
POLL_SECONDS = 5                        # how often to re-check Teams status

# --- Colors (R, G, B). None = turn the light OFF. ---
COLORS = {
    "available": (0, 255, 0),     # green
    "busy":      (255, 0, 0),     # red
    "away":      (255, 255, 0),   # yellow
    "offline":   None,            # off
    "unknown":   None,            # off
}

# --- Map Teams "availability" strings -> our color buckets ---
# Teams presence values seen in logs / Graph: Available, Busy, BusyIdle,
# DoNotDisturb, Away, BeRightBack, AwayIdle, Offline, PresenceUnknown, etc.
AVAILABILITY_MAP = {
    "available": "available",
    "availableidle": "available",
    "green": "available",

    "busy": "busy",
    "busyidle": "busy",
    "donotdisturb": "busy",
    "inacall": "busy",
    "inameeting": "busy",
    "inaconferencecall": "busy",
    "onthephone": "busy",
    "presenting": "busy",
    "focusing": "busy",
    "urgentinterruptionsonly": "busy",

    "away": "away",
    "awayidle": "away",
    "berightback": "away",
    "inactive": "away",

    "offline": "offline",
    "offwork": "offline",
    "presenceunknown": "unknown",
}

# Teams new-client log location (MSIX package).
import os
TEAMS_LOG_DIR = os.path.join(
    os.environ["LOCALAPPDATA"],
    r"Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\Logs",
)

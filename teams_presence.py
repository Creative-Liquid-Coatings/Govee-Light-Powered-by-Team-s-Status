"""Read current Teams presence from the new-Teams local logs.

New Teams represents presence two ways in its logs:
  * `availability: Busy`                       (cloud/global state events)
  * `... status Do not disturb`  / `status Busy`  (taskbar overlay + badge)

DND in particular is ONLY emitted as the overlay form "status Do not disturb",
so we parse both. We scan the tail of the newest log, collect every token that
maps to a known presence bucket, and return the most recent one. Unknown
`status ...` lines (e.g. "status Connected") are ignored.
"""
import glob
import os
import re
import time
from config import TEAMS_LOG_DIR, AVAILABILITY_MAP, STALE_AFTER_SECONDS

# `availability: Busy`  OR  trailing `status Do not disturb` / `status Busy`
_AVAIL_RE = re.compile(r"availability:\s*([A-Za-z]+)")
_STATUS_RE = re.compile(r"\bstatus ([A-Za-z][A-Za-z ]*[A-Za-z])\s*$")

_TAIL_BYTES = 256 * 1024  # read last 256 KB of the active log


def _newest_log() -> str | None:
    files = glob.glob(os.path.join(TEAMS_LOG_DIR, "MSTeams_*.log"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def _normalize(token: str) -> str:
    return token.lower().replace(" ", "")


def get_availability() -> str | None:
    """Return a normalized bucket: available/busy/away/offline/unknown,
    or None if presence can't be determined OR the log is stale (Teams not
    actively running). Callers treat None as "turn the light off"."""
    path = _newest_log()
    if not path:
        return None
    try:
        # Stale log => Teams isn't actively running => no signal.
        if time.time() - os.path.getmtime(path) > STALE_AFTER_SECONDS:
            return None
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > _TAIL_BYTES:
                f.seek(size - _TAIL_BYTES)
            text = f.read().decode("utf-8", errors="ignore")
    except OSError:
        return None

    last_bucket = None
    for line in text.splitlines():
        candidates = _AVAIL_RE.findall(line) + _STATUS_RE.findall(line)
        for cand in candidates:
            bucket = AVAILABILITY_MAP.get(_normalize(cand))
            if bucket:                 # only accept recognized presence words
                last_bucket = bucket
    return last_bucket


if __name__ == "__main__":
    print("Newest log:", _newest_log())
    print("Current availability bucket:", get_availability())

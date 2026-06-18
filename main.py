"""Teams status -> Govee H6053 light.

Polls local Teams logs for your presence and sets the light color:
  Available -> green, Busy/DND/InACall -> red, Away -> amber, Offline -> off.

Run:  python main.py
Stop: Ctrl+C
"""
import asyncio
import os
from datetime import datetime

import govee_light
from config import COLORS, POLL_SECONDS
from teams_presence import get_availability

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime.log")


def log(msg: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    try:
        print(line, flush=True)          # no-op when run hidden (pythonw)
    except Exception:
        pass
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


async def main():
    log(f"Started. Polling every {POLL_SECONDS}s. Ctrl+C to stop.")
    last_bucket = None

    while True:
        bucket = get_availability()

        if bucket is None:
            # Teams not running / no log yet: leave the light as-is.
            log("presence: unknown (Teams not running?) - no change")
        elif bucket != last_bucket:
            rgb = COLORS.get(bucket, None)
            desc = "OFF" if rgb is None else f"RGB{rgb}"
            ok = await govee_light.apply(rgb)
            status = "ok" if ok else "FAILED"
            log(f"presence: {bucket}  ->  {desc}  [{status}]")
            if ok:
                last_bucket = bucket
            # if it failed, leave last_bucket unchanged so we retry next poll
        # else: no change, do nothing

        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")

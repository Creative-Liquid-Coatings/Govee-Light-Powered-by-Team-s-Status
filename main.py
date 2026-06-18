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
    last_target = None

    while True:
        bucket = get_availability()
        # No fresh presence (Teams idle/closed/signed out) -> turn OFF
        # rather than holding the last color.
        target = bucket if bucket else "offline"

        if target != last_target:
            rgb = COLORS.get(target)
            desc = "OFF" if rgb is None else f"RGB{rgb}"
            reason = bucket if bucket else "no signal (Teams idle/closed)"
            ok = await govee_light.apply(rgb)
            status = "ok" if ok else "FAILED"
            log(f"presence: {reason}  ->  {desc}  [{status}]")
            if ok:
                last_target = target
            # if it failed, leave last_target unchanged so we retry next poll

        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Stopping - turning light off")
    finally:
        # Best-effort: turn the light off on graceful exit. (Won't run on a
        # hard kill or power-off, which BLE can't cover anyway.)
        try:
            asyncio.run(govee_light.apply(None))
        except Exception:
            pass

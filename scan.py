"""Scan for nearby BLE devices and highlight likely Govee lights.

Run with the H6053 powered ON and within ~10 m.
"""
import asyncio
from bleak import BleakScanner

GOVEE_HINTS = ("govee", "gbk", "ihoment", "gvh", "h6053", "minger")


async def main():
    print("Scanning for BLE devices for 12 seconds...\n")
    devices = await BleakScanner.discover(timeout=12.0, return_adv=True)

    rows = []
    for addr, (dev, adv) in devices.items():
        name = (dev.name or adv.local_name or "").strip()
        rows.append((adv.rssi, addr, name))

    rows.sort(reverse=True)  # strongest signal first

    print(f"{'RSSI':>5}  {'ADDRESS':<20}  NAME")
    print("-" * 60)
    for rssi, addr, name in rows:
        flag = "  <-- LIKELY GOVEE" if any(h in name.lower() for h in GOVEE_HINTS) else ""
        print(f"{rssi:>5}  {addr:<20}  {name or '(no name)'}{flag}")

    print("\nLook for a name containing 'Govee', 'GBK_H6053', 'ihoment_H6053', or similar.")
    print("Note its ADDRESS for the next step.")


if __name__ == "__main__":
    asyncio.run(main())

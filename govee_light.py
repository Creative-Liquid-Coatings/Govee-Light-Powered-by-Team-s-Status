"""Control the Govee H6053 over BLE.

Validated protocol: write 20-byte packets (payload padded to 19 bytes + XOR
checksum) to the control characteristic. Color uses the segmented RGBIC
sub-command 0x33 0x05 0x15.
"""
import asyncio
from bleak import BleakClient
from config import DEVICE_ADDRESS, BRIGHTNESS

WRITE_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11"


def _packet(*data: int) -> bytearray:
    pkt = bytearray(data)
    pkt += bytearray(19 - len(pkt))
    c = 0
    for b in pkt:
        c ^= b
    pkt.append(c)
    return pkt


def _power(on: bool) -> bytearray:
    return _packet(0x33, 0x01, 0x01 if on else 0x00)


def _brightness(level: int) -> bytearray:
    return _packet(0x33, 0x04, level & 0xFF)


def _color(r: int, g: int, b: int) -> bytearray:
    return _packet(0x33, 0x05, 0x15, 0x01, r, g, b, 0x00, 0x00, 0x00,
                   0x00, 0xFF, 0xFF, 0xFF, 0xFF)


async def apply(rgb: tuple[int, int, int] | None, retries: int = 3) -> bool:
    """Set the light to rgb, or turn it OFF if rgb is None.
    Opens a fresh BLE connection each call (robust against idle disconnects).
    Returns True on success."""
    for attempt in range(1, retries + 1):
        try:
            async with BleakClient(DEVICE_ADDRESS, timeout=20.0) as client:
                if rgb is None:
                    await client.write_gatt_char(WRITE_UUID, _power(False), response=False)
                else:
                    await client.write_gatt_char(WRITE_UUID, _power(True), response=False)
                    await asyncio.sleep(0.15)
                    await client.write_gatt_char(WRITE_UUID, _brightness(BRIGHTNESS), response=False)
                    await asyncio.sleep(0.15)
                    await client.write_gatt_char(WRITE_UUID, _color(*rgb), response=False)
            return True
        except Exception as e:
            if attempt == retries:
                print(f"    [ble] failed after {retries} attempts: {type(e).__name__}: {e}")
                return False
            await asyncio.sleep(2)
    return False


if __name__ == "__main__":
    # quick manual test: cycle colors
    async def _demo():
        for name, rgb in (("red", (255, 0, 0)), ("green", (0, 255, 0)),
                          ("amber", (255, 170, 0)), ("off", None)):
            print("set", name, "->", await apply(rgb))
            await asyncio.sleep(2)
    asyncio.run(_demo())

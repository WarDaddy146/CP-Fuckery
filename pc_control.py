"""
pc_control.py — run this on your PC (not on the board) to control the
LED over the raw-HID channel exposed by code.py.

Install:
    pip install hid

On Linux you also need the hidapi system lib:
    sudo apt install libhidapi-hidraw0          # Debian/Ubuntu
On macOS: works out of the box.
On Windows: works out of the box.

Linux permissions: by default /dev/hidraw* is root-only. Either run with
sudo, or drop a udev rule. For Adafruit CircuitPython boards (VID 0x239A)
something like:

    # /etc/udev/rules.d/99-circuitpython-hid.rules
    SUBSYSTEM=="hidraw", ATTRS{idVendor}=="239a", MODE="0666"

then `sudo udevadm control --reload && sudo udevadm trigger`.
"""

import sys
import time
import hid

# CircuitPython's default vendor ID is Adafruit's. The PID depends on
# which board you're using. If you don't know yours, run this file with
# `--list` to see all attached HID devices.
ADAFRUIT_VID = 0x239A

# Our raw-HID interface advertises this usage page/usage (must match boot.py).
RAW_USAGE_PAGE = 0xFF00
RAW_USAGE      = 0x01

# Command bytes — keep in sync with code.py
CMD_SET_LED   = 0x01
CMD_GET_LED   = 0x02
CMD_PING      = 0x03
CMD_PULSE_LED = 0x04


def list_devices():
    print(f"{'VID':>6} {'PID':>6}  {'usage_page':>10} {'usage':>6}  product")
    for d in hid.enumerate():
        print(f"  {d['vendor_id']:#06x} {d['product_id']:#06x}  "
              f"{d['usage_page']:#010x} {d['usage']:#06x}  "
              f"{d.get('product_string','')}")


def find_raw_hid():
    """Find the right HID interface (vendor page) on the CircuitPython board."""
    for d in hid.enumerate():
        if (d['vendor_id'] == ADAFRUIT_VID
                and d['usage_page'] == RAW_USAGE_PAGE
                and d['usage'] == RAW_USAGE):
            return d
    return None


class Board:
    def __init__(self):
        info = find_raw_hid()
        if info is None:
            raise RuntimeError(
                "Raw HID interface not found. Make sure boot.py is installed "
                "on the board and that you've unplugged + replugged it. "
                "Run with --list to see what HID interfaces are visible."
            )
        self.dev = hid.Device(path=info['path'])

    def close(self):
        self.dev.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _send(self, payload):
        """Send a 64-byte OUT report (prefixed with report-ID 0)."""
        buf = bytearray(65)              # 1 byte report ID + 64 bytes data
        buf[1:1 + len(payload)] = payload
        self.dev.write(bytes(buf))

    def _recv(self, timeout_ms=500):
        data = self.dev.read(64, timeout=timeout_ms)
        return bytes(data) if data else None

    # ---- High-level commands -------------------------------------------------
    def set_led(self, on: bool) -> bool:
        self._send(bytes((CMD_SET_LED, 1 if on else 0)))
        reply = self._recv()
        return bool(reply and reply[0] == CMD_SET_LED and reply[1])

    def get_led(self) -> bool:
        self._send(bytes((CMD_GET_LED,)))
        reply = self._recv()
        if not reply or reply[0] != CMD_GET_LED:
            raise RuntimeError(f"Unexpected reply: {reply!r}")
        return bool(reply[1])

    def pulse_led(self, duration_ms: int) -> None:
        duration_ms = max(0, min(0xFFFF, duration_ms))
        self._send(bytes((CMD_PULSE_LED, (duration_ms >> 8) & 0xFF, duration_ms & 0xFF)))
        self._recv()  # ack


def demo():
    with Board() as b:
        print("Ping:", b.ping(b"hi there"))
        print("LED was:", b.get_led())
        print("Turning LED on...")
        b.set_led(True)
        time.sleep(1.0)
        print("Turning LED off...")
        b.set_led(False)
        time.sleep(0.3)
        print("Pulsing for 500 ms...")
        b.pulse_led(500)
        time.sleep(1.0)
        print("Done. LED state now:", b.get_led())


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_devices()
    else:
        demo()

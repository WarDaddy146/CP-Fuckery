import board
import digitalio
import time
import usb_hid

# --- LED ---------------------------------------------------------------
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# --- Find the raw HID device registered by boot.py --------------------
raw_hid = None
for dev in usb_hid.devices:
    if dev.usage_page == 0xFF00 and dev.usage == 0x01:
        raw_hid = dev
        break

if raw_hid is None:
    print("Raw HID NOT found — is boot.py installed and did you replug?")
else:
    print("Raw HID ready.")

# --- Commands ---------------------------------------------------------
CMD_SET_LED = 0x01
CMD_GET_LED = 0x02
CMD_PING    = 0x03

def reply(payload):
    buf = bytearray(64)
    buf[:len(payload)] = payload
    try:
        raw_hid.send_report(buf)
    except OSError:
        pass

def handle_hid():
    if raw_hid is None:
        return
    r = raw_hid.get_last_received_report()
    if r is None:
        return
    cmd = r[0]
    if cmd == CMD_SET_LED:
        led.value = bool(r[1])
        reply(bytes((CMD_SET_LED, 1 if led.value else 0)))
    elif cmd == CMD_GET_LED:
        reply(bytes((CMD_GET_LED, 1 if led.value else 0)))
    elif cmd == CMD_PING:
        reply(bytes((CMD_PING,)) + bytes(r[1:32]))
    else:
        reply(bytes((0xFF, cmd)))

# --- Main loop --------------------------------------------------------
while True:
    handle_hid()
    time.sleep(0.01)

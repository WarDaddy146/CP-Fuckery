import hid
import time
from PIL import Image

# --- Image → cbuf ---
img = Image.open("ss.png").convert("L")   # convert to grayscale
img = img.resize((128, 32), Image.LANCZOS)         # resize to display resolution
cbuf = bytearray(b ^ 0xFF for b in img.tobytes())  # invert: dark→on, light→off

# --- HID send ---
for d in hid.enumerate():
    if d['usage_page'] == 0xFF00 and d['usage'] == 0x01:
        dev = hid.Device(path=d['path'])
        break
else:
    print("no device")
    exit(1)

for i in range(64):
    pkt = bytes(cbuf[i*64:(i+1)*64])
    dev.write(b'\x00' + pkt)
    print(f"[TX] packet {i}: {pkt.hex()}")
    time.sleep(0.005)

print("[TX] Done — 64 packets sent (4096 bytes)")
import hid
import sys
import time

RAW_USAGE_PAGE = 0xFF00
RAW_USAGE = 0x01

dev = None
for d in hid.enumerate():
    if d['usage_page'] == RAW_USAGE_PAGE and d['usage'] == RAW_USAGE:
        try:
            dev = hid.Device(path=d['path'])
            print(f"Connected: {d.get('product_string','')} ({d['vendor_id']:#06x}:{d['product_id']:#06x})")
            break
        except hid.HIDException as e:
            print(f"Found but can't open: {d.get('product_string','')} — {e}")
            print("Try: sudo python pc_control.py")

if dev is None:
    print("No raw HID device found.")
    sys.exit(1)

pixel_data = bytearray(512)

if '--fill' in sys.argv:
    pixel_data[:] = b'\xFF' * 512
elif len(sys.argv) >= 3:
    idx = int(sys.argv[1])
    val = int(sys.argv[2])
    pixel_data[idx] = val
    print(f"pixel_data[{idx}] = {val}")
else:
    pixel_data[46] = 0b00000100

for page in range(8):
    chunk = bytearray(64)
    chunk[0] = page
    chunk[1:64] = pixel_data[page * 64 + 1 : (page + 1) * 64]
    dev.write(b'\x00' + bytes(chunk))
    time.sleep(0.01)

chunk = bytearray(64)
chunk[0] = 0xFF
for i in range(8):
    chunk[1 + i] = pixel_data[i * 64]
dev.write(b'\x00' + bytes(chunk))

dev.close()

import usb_hid
import board
import busio

OLED_ADDR = 0x3C

i2c = busio.I2C(scl=board.P0_22, sda=board.P0_20, frequency=400000)
while not i2c.try_lock():
    pass

def cmd(c):
    i2c.writeto(OLED_ADDR, bytes([0x00, c]))

for c in [
    0xAE, 0xD5, 0x80, 0xA8, 0x1F, 0xD3, 0x00, 0x40,
    0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x02,
    0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF,
]:
    cmd(c)

for c in [0x21, 0, 127, 0x22, 0, 3]:
    cmd(c)

fb = bytearray(512)

raw_hid = None
for dev in usb_hid.devices:
    if dev.usage_page == 0xFF00 and dev.usage == 0x01:
        raw_hid = dev
        break

while True:
    r = raw_hid.get_last_received_report()
    if r is not None and len(r) == 64:
        page = r[0]
        if page < 8:
            fb[page * 64 + 1 : (page + 1) * 64] = r[1:64]
        elif page == 0xFF:
            for i in range(8):
                fb[i * 64] = r[1 + i]
            for offset in range(0, 512, 32):
                i2c.writeto(OLED_ADDR, bytes([0x40]) + fb[offset:offset + 32])

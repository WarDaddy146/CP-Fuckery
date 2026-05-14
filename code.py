import board
import busio
import digitalio
import time
from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.P0_22, board.P0_20)
mcp = MCP23017(i2c, address=0x20)

# GPA0-GPA7 = columns (inputs with pull-up)
cols = []
for c in range(8):
    pin = mcp.get_pin(c)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    cols.append(pin)

# GPB0-GPB7 = rows (outputs, driven LOW one at a time)
rows = []
for r in range(8):
    pin = mcp.get_pin(r + 8)
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = True
    rows.append(pin)

print("MCP23017 8x8 matrix keypad: GPA0-7=cols(inputs), GPB0-7=rows(outputs, active LOW)")

KEY_MAP = [
    ["1", "2", "3", "A", "Q", "W", "E", "R"],
    ["4", "5", "6", "B", "S", "D", "F", "T"],
    ["7", "8", "9", "C", "G", "H", "J", "Y"],
    ["*", "0", "#", "D", "K", "L", "Z", "U"],
    ["I", "O", "P", "Fn", "N", "M", "X", "V"],
    ["Up", "Dn", "Lt", "Rt", "Ent", "Spc", "Bk", "Tab"],
    ["A0", "A1", "A2", "A3", "B0", "B1", "B2", "B3"],
    ["C0", "C1", "C2", "C3", "D0", "D1", "D2", "D3"],
]

def scan_matrix():
    # all rows HIGH (inactive)
    gpio = 0xFF00
    mcp.gpio = gpio

    for row_idx in range(8):
        # drive this row LOW, keep others HIGH
        gpio = 0xFF00
        gpio &= ~(1 << ((row_idx + 3) % 8 + 8))
        mcp.gpio = gpio
        time.sleep(0.002)

        pins = mcp.gpio

        for col_idx in range(8):
            pressed = not (pins >> col_idx & 1)
            if pressed and not prev[row_idx][col_idx]:
                print(f"Key: {KEY_MAP[row_idx][col_idx]}  (col={col_idx}, row={row_idx})")
            prev[row_idx][col_idx] = pressed

        gpio |= 1 << ((row_idx + 3) % 8 + 8)
        mcp.gpio = gpio


prev = [[False]*8 for _ in range(8)]

while True:
    scan_matrix()
    time.sleep(0.02)

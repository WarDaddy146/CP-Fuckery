import board
import busio
import digitalio
import time
from adafruit_mcp230xx.mcp23017 import MCP23017

# ============================================================
# STEP 1: Scan I2C bus to find connected devices
# ============================================================
# REPL:
#   >>> import board, busio
#   >>> i2c = busio.I2C(board.P0_04, board.P0_03)  # SCL=GP4, SDA=GP3
#   >>> while not i2c.try_lock(): pass
#   >>> [hex(a) for a in i2c.scan()]
#   >>> i2c.unlock()
# You should see '0x20' if the MCP23017 is wired with A0/A1/A2 to GND.
# ============================================================

i2c = busio.I2C(board.P0_04, board.P0_03)  # SCL=GP4, SDA=GP3
mcp = MCP23017(i2c, address=0x20)

# ============================================================
# STEP 2: Configure GPA0 as input with pull-up
#          Configure GPB3 as output, driven LOW
# ============================================================
# REPL:
#   >>> btn = mcp.get_pin(0)         # GPA0
#   >>> btn.direction = digitalio.Direction.INPUT
#   >>> btn.pull = digitalio.Pull.UP
#   >>> btn.value                    # True = not pressed
#   >>> \
#   >>> drive = mcp.get_pin(11)      # GPB3 = pin 11
#   >>> drive.direction = digitalio.Direction.OUTPUT
#   >>> drive.value = False          # drive LOW
#   >>> drive.value                  # confirm 0
# When GPA0 and GPB3 are shorted: btn.value → False
# ============================================================

btn = mcp.get_pin(0)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP

drive = mcp.get_pin(11)
drive.direction = digitalio.Direction.OUTPUT
drive.value = False

# ============================================================
# STEP 3: Read raw register values to verify configuration
# ============================================================
# REPL:
#   >>> mcp.iodir  # 0bXXXXXXXX_XXXXXXXX
#                  #   lower byte = GPA: bit0=1 (input)
#                  #   upper byte = GPB: bit3=0 (output)
#   >>> mcp.gppu   # pull-up: lower byte bit0=1
#   >>> mcp.gpio   # live states: lower byte bit0 reads GPA0
#   >>> mcp.gpio  & 0x0800  # GPB3 state in upper byte
# ============================================================

print("MCP23017 button demo: short GPB3 ↔ GPA0 to trigger...")

# ============================================================
# STEP 4: Poll for short between GPB3 (LOW) and GPA0
# ============================================================
# REPL:
#   >>> btn.value   # True = open, False = shorted to GPB3
# ============================================================

while True:
    if not btn.value:
        print("pressed")
        time.sleep(0.3)
    time.sleep(0.05)

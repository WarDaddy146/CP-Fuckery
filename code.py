import board
import busio
import time
from ina226 import INA226

# ── Setup ─────────────────────────────────────────────────────────────────────
i2c = busio.I2C(board.GP3, board.GP2)   # SCL=GP3, SDA=GP2
sensor = INA226(i2c, 0x44, r_shunt=10.0, max_current=0.01)

print("INA226 ready. Starting measurements...\n")

# ── Main loop ─────────────────────────────────────────────────────────────────
while True:
    current_ua = sensor.current_mA
    print(f"Shunt: {sensor.shunt_voltage_mV:.6f} mV | Current: {current_ua:.6f} µA")
    time.sleep(1)

# ina226.py — Minimal CircuitPython driver for the INA226
# Drop this into /lib/ on your CIRCUITPY drive.
# Works with CircuitPython's busio.I2C (NOT MicroPython machine.I2C).
#
# Wiring:
#   VCC  → 3.3V
#   GND  → GND
#   SDA  → GP2 (or any SDA pin)
#   SCL  → GP3 (or any SCL pin)
#   VIN+ / VIN- in series with load's power rail
#
# Usage:
#   from ina226 import INA226
#   sensor = INA226(i2c, address=0x40, r_shunt=0.1, max_current=0.5)
#   print(sensor.bus_voltage_V)
#   print(sensor.current_mA)

# ── Register map ──────────────────────────────────────────────────────────────
_REG_CONFIG      = 0x00
_REG_SHUNT_V     = 0x01
_REG_BUS_V       = 0x02
_REG_POWER       = 0x03
_REG_CURRENT     = 0x04
_REG_CALIBRATION = 0x05

# ── CONFIG register defaults ───────────────────────────────────────────────────
# AVG=16 samples | VBUSCT=1.1ms | VSHCT=1.1ms | Mode=shunt+bus continuous
_DEFAULT_CONFIG = 0x4527


class INA226:
    """
    Lightweight CircuitPython driver for the INA226 power monitor.

    Parameters
    ----------
    i2c        : busio.I2C instance
    address    : I2C address (default 0x40)
    r_shunt    : Shunt resistance in ohms (check your breakout — commonly 0.1 Ω)
    max_current: Maximum expected current in amps (sets ADC resolution)
    """

    def __init__(self, i2c, address=0x40, r_shunt=0.1, max_current=0.5):
        self._i2c    = i2c
        self._addr   = address
        self._r_shunt = r_shunt

        # Current LSB = max_current / 2^15
        self._current_lsb = max_current / 32768

        # Calibration register value = 0.00512 / (current_lsb * r_shunt)
        cal = int(0.00512 / (self._current_lsb * r_shunt))
        self._write_reg(_REG_CALIBRATION, cal)
        self._write_reg(_REG_CONFIG, _DEFAULT_CONFIG)

    # ── Low-level I2C ─────────────────────────────────────────────────────────

    def _write_reg(self, reg, value):
        buf = bytes([reg, (value >> 8) & 0xFF, value & 0xFF])
        while not self._i2c.try_lock():
            pass
        try:
            self._i2c.writeto(self._addr, buf)
        finally:
            self._i2c.unlock()

    def _read_reg(self, reg):
        out = bytearray(2)
        while not self._i2c.try_lock():
            pass
        try:
            self._i2c.writeto(self._addr, bytes([reg]))
            self._i2c.readfrom_into(self._addr, out)
        finally:
            self._i2c.unlock()
        return (out[0] << 8) | out[1]

    def _signed(self, raw):
        """Convert 16-bit unsigned to signed integer."""
        return raw if raw < 0x8000 else raw - 0x10000

    # ── Measurement properties ────────────────────────────────────────────────

    @property
    def bus_voltage_V(self):
        """Bus voltage in volts. LSB = 1.25 mV."""
        raw = self._read_reg(_REG_BUS_V)
        return raw * 1.25e-3

    @property
    def shunt_voltage_mV(self):
        """Shunt voltage in millivolts. LSB = 2.5 µV."""
        raw = self._signed(self._read_reg(_REG_SHUNT_V))
        return raw * 2.5e-3  # 2.5 µV → mV

    @property
    def current_mA(self):
        """Current in milliamps (signed — negative if reversed)."""
        raw = self._signed(self._read_reg(_REG_CURRENT))
        return raw * self._current_lsb * 1000

    @property
    def power_mW(self):
        """Power in milliwatts. Power LSB = 25 × current_lsb."""
        raw = self._read_reg(_REG_POWER)
        return raw * 25 * self._current_lsb * 1000

    def read_all(self):
        """Return (bus_V, shunt_mV, current_mA, power_mW) in one call."""
        return (
            self.bus_voltage_V,
            self.shunt_voltage_mV,
            self.current_mA,
            self.power_mW,
        )
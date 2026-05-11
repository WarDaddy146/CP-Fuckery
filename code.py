import board
import digitalio
import time
pins = [
    board.P0_02, board.P0_04, board.P0_06, board.P0_08,
    board.P0_09, board.P0_10, board.P0_11, board.P0_12,
    board.P0_13, board.P0_15, board.P0_17, board.P0_20,
    board.P0_22, board.P0_24, board.P0_26, board.P0_29,
    board.P0_31, board.P1_00, board.P1_01, board.P1_02,
    board.P1_04, board.P1_06, board.P1_07, board.P1_11,
    board.P1_13, board.P1_15, board.LED, board.VCC_OFF,
    board.BAT_VOLT, board.NFC1, board.NFC2,
]

for p in pins:
    if p is not None:
        try:
            d = digitalio.DigitalInOut(p)
            d.direction = digitalio.Direction.OUTPUT
            d.value = True
        except Exception:
            pass
        time.sleep(1000)

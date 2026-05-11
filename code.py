import board
import neopixel
import time

# Change the 1 to however many LEDs you have!
# Example: neopixel.NeoPixel(board.GP2, 30, brightness=0.1)
pixel = neopixel.NeoPixel(board.D2, 1, brightness=0.9)

# pixel[0] lights up the first LED
# pixel[1] lights up the second LED
# pixel[2] lights up the third LED... and so on!

while True:
    print("Turning on the LED")
    pixel[0] = (255, 0, 0)
    time.sleep(10)
    print("Turning off the LED")
    pixel[0] = (0, 0, 0)
    time.sleep(1)
import board
import neopixel
import time

# Change the 1 to however many LEDs you have!
# Example: neopixel.NeoPixel(board.GP2, 30, brightness=0.1)
pixel = neopixel.NeoPixel(board.P0_06, 5, brightness=0.9)

# pixel[0] lights up the first LED
# pixel[1] lights up the second LED
# pixel[2] lights up the third LED... and so on!

while True:
    print("Red")
    pixel[0] = (255, 0, 0)
    time.sleep(10)
    print("Green")
    pixel[1] = (0, 255, 0)
    time.sleep(1)
    print("Blue")
    pixel[2] = (0, 0, 255)
    time.sleep(1)
    print("White")
    pixel[3] = (255, 255, 255)
    time.sleep(1)
    print("Off")
    pixel[4] = (0, 0, 0)
    time.sleep(1)
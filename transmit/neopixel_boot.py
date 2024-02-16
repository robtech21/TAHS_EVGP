#!/usr/bin/env python3

# Neopixel script for EVGP data system bootup
import board,neopixel,sys
from time import sleep
led_count = 4
pixels = neopixel.NeoPixel(board.D18,led_count)
pixels.brightness = 0.1

timer = 10
for arg in sys.argv:
    if "time" in arg:
        timer = int(arg.split("=")[1])

def clear(color=(0,0,0),delay=float(0)):
    for i in range(0,led_count):
        pixels[i] = color
        #print(i)
        sleep(delay)

for i in range(0,timer):
    clear(color=(0,0,0))
    sleep(0.1)
    clear(color=(255,255,0),delay=0.05)
    sleep(1)

clear(color=(255,0,0),delay=0.02)

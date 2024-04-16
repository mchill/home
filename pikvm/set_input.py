# Credits to @mharsch for reverse engineering the controller behavior
# https://gist.github.com/mharsch/52b0a99a945711385fb0120020d8226d

import RPi.GPIO as GPIO
import sys
import time

input_pin = 23  # connected to 'D+' pin on mini USB
output_pin = 24  # connected to 'D-' pin on mini USB


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(input_pin, GPIO.IN)
    GPIO.setup(output_pin, GPIO.OUT)
    GPIO.output(output_pin, GPIO.HIGH)


def get_port() -> int:
    while GPIO.input(input_pin) == GPIO.LOW:
        time.sleep(0.001)
    while GPIO.input(input_pin) == GPIO.HIGH:
        time.sleep(0.001)
    start = time.time()
    while GPIO.input(input_pin) == GPIO.LOW:
        time.sleep(0.001)
    stop = time.time()

    return round((stop - start) * 50)


def set_port(port: int):
    if get_port() == port:
        return

    GPIO.output(output_pin, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(output_pin, GPIO.HIGH)
    time.sleep(0.02)
    GPIO.output(output_pin, GPIO.LOW)
    time.sleep(0.02 * port)
    GPIO.output(output_pin, GPIO.HIGH)


setup()
set_port(int(sys.argv[1]))

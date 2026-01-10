import RPi.GPIO as GPIO
import time

BUTTON_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_button():
    return GPIO.input(BUTTON_PIN) == GPIO.LOW

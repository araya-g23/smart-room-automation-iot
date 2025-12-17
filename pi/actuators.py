import RPi.GPIO as GPIO

RELAY_PIN = 17  # GPIO17 = PIN 11

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)


def turn_light_on():
    """Turn the light on by activating the relay."""
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Assuming LOW activates the relay


def turn_light_off():
    """Turn the light off by deactivating the relay."""
    GPIO.output(RELAY_PIN, GPIO.HIGH)


def cleanup():
    """Clean up GPIO settings."""
    GPIO.cleanup()

import RPi.GPIO as GPIO
import board
import adafruit_dht

# GPIO pin
PIR_PIN = 6
#DHT_PIN = 4
LDR_PIN = 24

dhtDevice = adafruit_dht.DHT22(board.D4)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LDR_PIN, GPIO.IN)


def read_pir():
    """Read the PIR sensor state."""
    return GPIO.input(PIR_PIN)


def read_ldr():
    """Read the LDR sensor state."""
    return GPIO.input(LDR_PIN)

def read_dht():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return temperature, humidity
    except RuntimeError:
        return None, None
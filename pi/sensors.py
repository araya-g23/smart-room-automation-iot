import RPi.GPIO as GPIO
import Adafruit_DHT

# GPIO pin
PIR_PIN = 6
DHT_PIN = 4
LDR_PIN = 24

DHT_SENSOR = Adafruit_DHT.DHT22

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
    """Read the DHT22 sensor for temperature and humidity."""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return humidity, temperature

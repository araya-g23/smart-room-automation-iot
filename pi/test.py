import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

RELAY_PIN = 17  # GPIO17 = PIN 11
GPIO.setup(RELAY_PIN, GPIO.OUT)

print("Relay test running... Press CTRL+C to stop.")

try:
    while True:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("Relay ON - LED should be ON")
        time.sleep(2)

        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("Relay OFF - LED should be OFF")
        time.sleep(2)


except KeyboardInterrupt:
    GPIO.cleanup()
    print("Stopped.")

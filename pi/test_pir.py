import RPi.GPIO as GPIO
import time

PIR_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

print("PIR sensor test started")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("Motion detected!")
        else:
            print("No motion")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Stopped")

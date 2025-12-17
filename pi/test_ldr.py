import RPi.GPIO as GPIO
import time

LDR_PIN = 24  

GPIO.setmode(GPIO.BCM)
GPIO.setup(LDR_PIN, GPIO.IN)

print("LDR test started")

try:
    while True:
        if GPIO.input(LDR_PIN):
            print("Bright")
        else:
            print("Dark")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Stopped")

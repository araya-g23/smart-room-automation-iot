import RPi.GPIO as GPIO
import time

BUTTON_PIN = 27
RELAY_PIN = 17

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, GPIO.LOW)  # light OFF initially
light_on = False

print("Button + Relay test started")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            light_on = not light_on

            if light_on:
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                print("Light ON (physical button)")
            else:
                GPIO.output(RELAY_PIN, GPIO.LOW)
                print("Light OFF (physical button)")

            time.sleep(0.4)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nCleaning up GPIO")
    GPIO.cleanup()

import time
from sensors import read_pir, read_ldr, read_dht
from actuators import turn_light_off, turn_light_on, cleanup

print("Home Automation System Starting...")

try:
    while True:
        motion = read_pir()
        light =read_ldr()
        temp, hum = read_dht()

        data = {
            "motion": bool(motion),
            "light": "bright" if light else "dark",
            "temperature": temp,
            "humidity": hum,
        }

        print(f"Sensor Data: {data}")
        if motion and not light:
            print("Motion detected in dark environment. Turning light ON.")
            turn_light_on()
        
        # elif light:
        #     print("Environment is bright. Turning light OFF.")
        #     turn_light_off()
        else:
            print("No motion or sufficient light. Turning light OFF.")
            turn_light_off()

        time.sleep(2)

except KeyboardInterrupt:
    cleanup()
    print("Shutting down Home Automation System...")

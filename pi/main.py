import time
from sensors import read_pir, read_ldr, read_dht
from actuators import turn_light_off, turn_light_on, cleanup
from pubnub.pubnub_client import publish_sensor_data, start_control_listener


print("Home Automation System Starting...")


def handle_control_command(command):
    if command == "TURN_LIGHT_ON":
        turn_light_on()
        print("Light turned ON via remote command.")
    elif command == "TURN_LIGHT_OFF":
        turn_light_off()
        print("Light turned OFF via remote command.")


start_control_listener(handle_control_command)

try:
    while True:
        motion = read_pir()
        light = read_ldr()
        temp, hum = read_dht()

        data = {
            "motion": bool(motion),
            "light": "bright" if light else "dark",
            "temperature": temp,
            "humidity": hum,
        }
        publish_sensor_data(data)

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

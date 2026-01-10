import time
from sensors import read_pir, read_ldr, read_dht
from actuators import turn_light_off, turn_light_on, cleanup
from pubnub_client import publish_sensor_data, start_control_listener
from button import read_button


print("Home Automation System Starting...")

PUBLISH_INTERVAL = 60
last_publish_time = 0
last_light_state = None


def handle_control_command(command):
    global last_light_state
    if command == "TURN_LIGHT_ON":
        turn_light_on()
        last_light_state = True
        print("Light turned ON via remote command.")
        publish_sensor_data(get_sensor_snapshot())

    elif command == "TURN_LIGHT_OFF":
        turn_light_off()
        last_light_state = False
        print("Light turned OFF via remote command.")
        publish_sensor_data(get_sensor_snapshot())


def get_sensor_snapshot(event=None):
    motion = read_pir()
    light = read_ldr()
    temp, hum = read_dht()

    data = {
        "motion": bool(motion),
        "light": "bright" if light else "dark",
        "temperature": temp,
        "humidity": hum,
    }

    if event:
        data["event"] = event

    return data


start_control_listener(handle_control_command)

try:
    while True:
        data = get_sensor_snapshot()
        motion = data["motion"]
        light_is_bright = data["light"] == "bright"

        now = time.time()
        should_publish = False

        if read_button():
            if last_light_state:
                turn_light_off()
                last_light_state = False
                print("Light OFF via physical button")

                publish_sensor_data(
                    get_sensor_snapshot(event="Light OFF via physical button")
                )
            else:
                turn_light_on()
                last_light_state = True
                print("Light ON via physical button")

                publish_sensor_data(
                    get_sensor_snapshot(event="Light ON via physical button")
                )
            time.sleep(0.5)

        # immediate publish
        if motion:
            should_publish = True

        # Light control logic
        if motion and not light_is_bright:
            print("Motion detected in dark environment. Turning light ON.")
            turn_light_on()
            if last_light_state is not True:
                last_light_state = True
                should_publish = True

        else:
            print("No motion or sufficient light. Turning light OFF.")
            turn_light_off()
            if last_light_state is not False:
                last_light_state = False
                should_publish = True

        # update every 60 seconds
        if now - last_publish_time >= PUBLISH_INTERVAL:
            should_publish = True

        if should_publish:
            publish_sensor_data(data)
            last_publish_time = now
            print("Sensor data published")

        print(f"Sensor Data: {data}")
        time.sleep(1)

except KeyboardInterrupt:
    cleanup()
    print("Shutting down Home Automation System...")

# https://www.pubnub.com/docs/sdks/python

import os
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback

from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)


PUBLISH_KEY = os.getenv("PUBNUB_PUBLISH_KEY")
SUBSCRIBE_KEY = os.getenv("PUBNUB_SUBSCRIBE_KEY")
PI_TOKEN = os.getenv("PUBNUB_PI_TOKEN")
print("PI TOKEN FROM ENV:", PI_TOKEN)
print("PI TOKEN LENGTH:", len(PI_TOKEN))


if not PUBLISH_KEY or not SUBSCRIBE_KEY or not PI_TOKEN:
    raise ValueError("Missing PubNub keys/token in .env")

pnconfig = PNConfiguration()
pnconfig.publish_key = PUBLISH_KEY
pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.uuid = "raspberry-pi-01"

pubnub = PubNub(pnconfig)


pubnub.set_token(PI_TOKEN)


CONTROL_CALLBACK = None


class ControlListener(SubscribeCallback):
    def message(self, pubnub, message):
        if CONTROL_CALLBACK:
            CONTROL_CALLBACK(message.message)


def start_control_listener(callback):
    global CONTROL_CALLBACK
    CONTROL_CALLBACK = callback
    pubnub.add_listener(ControlListener())
    pubnub.subscribe().channels("home-automation-control").execute()


def publish_sensor_data(data):
    pubnub.publish().channel("home-automation-sensor-data").message(data).sync()

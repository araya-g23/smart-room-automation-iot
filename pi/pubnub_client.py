# https://www.pubnub.com/docs/sdks/python

import os
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback

# load environment variables
load_dotenv()

PUBLISH_KEY = os.getenv("PUBNUB_PUBLISH_KEY")
SUBSCRIBE_KEY = os.getenv("PUBNUB_SUBSCRIBE_KEY")
PI_TOKEN = os.getenv("PUBNUB_PI_TOKEN")

if not PUBLISH_KEY or not SUBSCRIBE_KEY:
    raise ValueError("PubNub keys are not set in environment variables.")

pnconfig = PNConfiguration()
pnconfig.publish_key = PUBLISH_KEY
pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.uuid = "raspberry-pi-01"
pnconfig.auth_key = PI_TOKEN

pubnub = PubNub(pnconfig)

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

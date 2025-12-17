import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback

# Load environment variables
load_dotenv()

PUBLISH_KEY = os.getenv("PUBNUB_PUBLISH_KEY")
SUBSCRIBE_KEY = os.getenv("PUBNUB_SUBSCRIBE_KEY")

if not PUBLISH_KEY or not SUBSCRIBE_KEY:
    raise ValueError("PubNub keys are not set in environment variables.")

app = Flask(__name__)

latest_data = {}

# PubNub configuration
pnconfig = PNConfiguration()
pnconfig.publish_key = PUBLISH_KEY
pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.uuid = "home-automation-server"

pubnub = PubNub(pnconfig)


class SensorDataListener(SubscribeCallback):
    def message(self, pubnub, message):
        global latest_data
        if message.channel == "home-automation-sensor-data":
            latest_data = message.message


# start PubNub listener
pubnub.add_listener(SensorDataListener())
pubnub.subscribe().channels("home-automation-sensor-data").execute()


@app.route("/")
def dashboard():
    return render_template("dashboard.html", data=latest_data)


@app.route("/on", methods=["POST"])
def light_on():
    pubnub.publish().channel("home-automation-control").message("TURN_LIGHT_ON").sync()
    return redirect("/")


@app.route("/off", methods=["POST"])
def light_off():
    pubnub.publish().channel("home-automation-control").message("TURN_LIGHT_OFF").sync()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

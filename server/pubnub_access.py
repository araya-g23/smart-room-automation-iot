import os
from dotenv import load_dotenv
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.models.consumer.v3.channel import Channel

load_dotenv()


def get_pubnub_admin():
    pnconfig = PNConfiguration()
    pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
    pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
    pnconfig.secret_key = os.getenv("PUBNUB_SECRET_KEY")
    pnconfig.uuid = "server-auth"
    return PubNub(pnconfig)


def generate_user_token(user_id, role="user"):
    pubnub = get_pubnub_admin()

    channels = [Channel.id("home-automation-sensor-data").read()]

    if role == "admin":
        channels.append(Channel.id("home-automation-control").read().write())

    envelope = (
        pubnub.grant_token()
        .channels(channels)
        .authorized_uuid(str(user_id))
        .ttl(60)
        .sync()
    )

    return envelope.result.token


def generate_pi_token():
    pubnub = get_pubnub_admin()

    envelope = (
        pubnub.grant_token()
        .authorized_uuid("raspberry-pi-01")
        .ttl(1440)  # 24 hours
        .channels(
            [
                Channel.id("home-automation-sensor-data").write(),
                Channel.id("home-automation-control").read(),
            ]
        )
        .sync()
    )

    return envelope.result.token

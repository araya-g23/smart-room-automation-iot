import os
import time
from dotenv import load_dotenv
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.models.consumer.v3.channel import Channel
from pubnub.exceptions import PubNubException

load_dotenv()

# cached server client
_server_pubnub = None
_server_token_expiry = 0


def get_pubnub_admin():
    pnconfig = PNConfiguration()
    pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
    pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
    pnconfig.secret_key = os.getenv("PUBNUB_SECRET_KEY")
    pnconfig.uuid = "server-auth"
    return PubNub(pnconfig)


def get_server_pubnub():
    """
    Server-side PubNub client with auto token refresh
    """
    global _server_pubnub, _server_token_expiry

    now = int(time.time())

    # Reuse token if still valid
    if _server_pubnub and now < _server_token_expiry:
        return _server_pubnub

    pubnub = get_pubnub_admin()

    try:
        envelope = (
            pubnub.grant_token()
            .authorized_uuid("home-automation-server")
            .ttl(60)
            .channels(
                [
                    Channel.id("home-automation-sensor-data").read(),
                    Channel.id("home-automation-control").write(),
                ]
            )
            .sync()
        )

        pubnub.set_token(envelope.result.token)

        # Refresh 5 minutes before expiry
        _server_token_expiry = now + (55 * 60)
        _server_pubnub = pubnub

        return pubnub

    except PubNubException as e:
        print("PubNub server token error:", e)
        return None


def generate_user_token(user_id, role, is_subscribed):
    pubnub = get_pubnub_admin()

    channels = [Channel.id("home-automation-sensor-data").read()]

    if role == "admin" or is_subscribed:
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


def generate_server_token():
    pubnub = get_pubnub_admin()

    envelope = (
        pubnub.grant_token()
        .authorized_uuid("home-automation-server")
        .ttl(1440)
        .channels(
            [
                Channel.id("home-automation-sensor-data").read(),
                Channel.id("home-automation-control").write(),
            ]
        )
        .sync()
    )

    return envelope.result.token

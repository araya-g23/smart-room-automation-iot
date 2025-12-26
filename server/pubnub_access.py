from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
import os

pnconfig = PNConfiguration()
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pnconfig.secret_key = os.getenv("PUBNUB_SECRET_KEY")  # REQUIRED
pnconfig.uuid = "server"

pubnub = PubNub(pnconfig)


def generate_user_token(user_id, role="user"):
    """
    Generate PubNub Access Manager token based on role
    """

    if role == "admin":
        resources = {
            "channels": {
                "home-automation-sensor-data": {"read": True, "write": True},
                "home-automation-control": {"read": True, "write": True},
            }
        }
    else:
        resources = {
            "channels": {
                "home-automation-sensor-data": {"read": True},
                "home-automation-control": {"read": False, "write": False},
            }
        }

    envelope = pubnub.grant_token(
        ttl=60,
        authorized_uuid=str(user_id),
        resources=resources,
        patterns={},
    ).sync()

    return envelope.result.token

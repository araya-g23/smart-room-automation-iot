import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, url_for, abort
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import db, User
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from functools import wraps


# Load environment variables
load_dotenv()

PUBLISH_KEY = os.getenv("PUBNUB_PUBLISH_KEY")
SUBSCRIBE_KEY = os.getenv("PUBNUB_SUBSCRIBE_KEY")
if not PUBLISH_KEY or not SUBSCRIBE_KEY:
    raise ValueError("PubNub keys are not set in environment variables.")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
print(DATABASE_URI)  # debug
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route("/on", methods=["POST"])
@login_required
@admin_required
def light_on():
    pubnub.publish().channel("home-automation-control").message("TURN_LIGHT_ON").sync()
    return redirect("/")


@app.route("/off", methods=["POST"])
@login_required
@admin_required
def light_off():
    pubnub.publish().channel("home-automation-control").message("TURN_LIGHT_OFF").sync()
    return redirect("/")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        return "Invalid login", 401

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

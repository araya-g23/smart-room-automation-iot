import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    abort,
    jsonify,
    session,
    Response,
)
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
from pubnub_access import generate_user_token, get_server_pubnub
from models import SensorLog
from utils.audit import log_action
from models import AuditLog
import csv
from io import StringIO
import time


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
# pnconfig = PNConfiguration()
# pnconfig.publish_key = PUBLISH_KEY
# pnconfig.subscribe_key = SUBSCRIBE_KEY
# pnconfig.uuid = "home-automation-server"

client = get_server_pubnub()
if not client:
    abort(503, description="Messaging service unavailable")


class SensorDataListener(SubscribeCallback):
    def message(self, pubnub, message):
        print("Received sensor data:", message.message)
        global latest_data

        if message.channel == "home-automation-sensor-data":
            latest_data = message.message
            latest_data["timestamp"] = time.time()

            with app.app_context():
                log = SensorLog(
                    motion=message.message.get("motion"),
                    light=message.message.get("light"),
                    temperature=message.message.get("temperature"),
                    humidity=message.message.get("humidity"),
                )
                db.session.add(log)
                db.session.commit()


# start PubNub listener
pubnub.add_listener(SensorDataListener())
pubnub.subscribe().channels("home-automation-sensor-data").execute()


@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        data=latest_data,
        server_time=time.time(),
    )


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def control_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)

        if current_user.role == "admin":
            return f(*args, **kwargs)

        # Check subscription status
        if getattr(current_user, "is_subscribed", False):
            return f(*args, **kwargs)

        abort(403)

    return decorated_function


@app.route("/on", methods=["POST"])
@login_required
@control_required
def light_on():

    client = get_pubnub_for_current_user()
    client.publish().channel("home-automation-control").message("TURN_LIGHT_ON").sync()

    log_action("Light turned ON")
    return redirect("/")


@app.route("/off", methods=["POST"])
@login_required
@control_required
def light_off():
    client = get_pubnub_for_current_user()
    client.publish().channel("home-automation-control").message("TURN_LIGHT_OFF").sync()

    log_action("Light turned OFF")
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
            token = generate_user_token(user.id, user.role, user.is_subscribed)
            session["pubnub_token"] = token
            log_action("User logged in")
            return redirect(url_for("dashboard"))

        return "Invalid login", 401

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered", 400

        new_user = User(email=email)
        new_user.set_password(password)
        new_user.role = "user"  # default role

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/admin/grant/<int:user_id>")
@login_required
def grant_pubnub_access(user_id):
    if current_user.role != "admin":
        return "Forbidden", 403

    user = User.query.get_or_404(user_id)
    token = generate_user_token(is_admin=(user.role == "admin"))

    return jsonify({"user": user.email, "pubnub_token": token})


def get_pubnub_for_current_user():
    token = session.get("pubnub_token")
    if not token:
        abort(403)

    pnconfig = PNConfiguration()
    pnconfig.publish_key = PUBLISH_KEY
    pnconfig.subscribe_key = SUBSCRIBE_KEY
    pnconfig.uuid = str(current_user.id)

    client = PubNub(pnconfig)
    client.set_token(token)

    try:
        client.publish().channel("home-automation-control").message("ping").sync()
    except Exception:
        abort(403, description="Subscription expired. Please contact admin.")
    return client


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/admin/audit-logs")
@login_required
@admin_required
def admin_audit_logs():
    page = request.args.get("page", 1, type=int)
    role = request.args.get("role", "")
    action = request.args.get("action", "")

    query = AuditLog.query

    if role:
        query = query.filter(AuditLog.role == role)

    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))

    pagination = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page,
        per_page=15,
        error_out=False,
    )

    return render_template(
        "admin_audit_logs.html",
        logs=pagination.items,
        pagination=pagination,
        role=role,
        action=action,
    )


@app.route("/admin/sensor-logs")
@login_required
@admin_required
def admin_sensor_logs():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    pagination = SensorLog.query.order_by(SensorLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "admin_sensor_logs.html",
        logs=pagination.items,
        pagination=pagination,
    )


@app.route("/admin/sensor-logs/export")
@login_required
@admin_required
def export_sensor_logs_csv():
    logs = SensorLog.query.order_by(SensorLog.created_at.desc()).all()

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(
        [
            "Time",
            "Motion",
            "Light",
            "Temperature",
            "Humidity",
        ]
    )

    for log in logs:
        writer.writerow(
            [
                log.created_at,
                log.motion,
                log.light,
                log.temperature,
                log.humidity,
            ]
        )

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sensor_logs.csv"},
    )


@app.route("/admin/audit-logs/export")
@login_required
@admin_required
def export_audit_logs_csv():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()

    si = StringIO()
    writer = csv.writer(si)

    # CSV header
    writer.writerow(
        [
            "ID",
            "User ID",
            "Role",
            "Action",
            "IP Address",
            "Timestamp",
        ]
    )

    for log in logs:
        writer.writerow(
            [
                log.id,
                log.user_id,
                log.role,
                log.action,
                log.ip_address,
                log.created_at,
            ]
        )

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )


@app.route("/admin/subscription/toggle/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_user_subscription(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        abort(400)

    user.is_subscribed = not user.is_subscribed
    db.session.commit()

    log_action(
        f"Subscription {'enabled' if user.is_subscribed else 'disabled'} for {user.email}"
    )

    return redirect(url_for("admin_users"))


@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@app.route("/logout")
@login_required
def logout():
    log_action("User logged out")
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

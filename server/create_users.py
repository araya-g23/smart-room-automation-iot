from app import app
from models import db, User

with app.app_context():
    # Create admin user
    admin = User(
        full_name="System Administrator",
        username="admin",
        email="admin@admin.com",
        role="admin",
        is_subscribed=True,
    )
    admin.set_password("Admin123@")

    # Create normal user
    user = User(
        full_name="Normal User",
        username="user",
        email="user@user.com",
        role="user",
        is_subscribed=False,
    )
    user.set_password("User123@")

    db.session.add(admin)
    db.session.add(user)
    db.session.commit()

print("Admin and user created successfully.")

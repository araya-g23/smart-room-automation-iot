from app import app
from models import db, User

with app.app_context():
    # Create admin
    admin = User(email="admin@admin.com", role="admin")
    admin.set_password("Admin123@")

    # Create normal user
    user = User(email="user@user.com", role="user")
    user.set_password("User123@")

    db.session.add(admin)
    db.session.add(user)
    db.session.commit()

print("Admin and user created successfully.")

from flask import request
from flask_login import current_user
from models import db, AuditLog


def log_action(action, user=None):
    log = AuditLog(
        user_id=(
            user.id
            if user
            else (current_user.id if current_user.is_authenticated else None)
        ),
        role=(
            user.role
            if user
            else (current_user.role if current_user.is_authenticated else None)
        ),
        action=action,
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()
    db.session.refresh(log)

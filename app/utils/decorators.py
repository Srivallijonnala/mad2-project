from functools import wraps
from flask import session, jsonify
from app.models import User


def get_current_user():
    """Return the logged-in User object based on the Flask session, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        if not user.is_active or user.is_blacklisted:
            return jsonify({"error": "Account deactivated/blacklisted"}), 403
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Restrict an endpoint to one or more roles, e.g. @role_required('admin')."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Authentication required"}), 401
            if not user.is_active or user.is_blacklisted:
                return jsonify({"error": "Account deactivated/blacklisted"}), 403
            if user.role not in roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

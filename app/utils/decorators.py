from functools import wraps
from flask import request, jsonify
from app.utils.jwt import decode_token
from app.utils.role import is_admin, is_user

# ---------------- Token ----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Login required"}), 401

        token = auth_header.split(" ")[1]
        valid, payload_or_message = decode_token(token)
        if not valid:
            return jsonify({"error": payload_or_message}), 401

        request.user = payload_or_message.get("data", {})
        return f(*args, **kwargs)
    return decorated

# ---------------- Roles ----------------
def roles_allowed(*allowed_roles):
    """Decorator to restrict routes based on role_name (case-insensitive)."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user:
                return jsonify({"error": "Login required"}), 401

            role_name = user.get("role_name", "")
            if not any(role_name.lower() == allowed.lower() for allowed in allowed_roles):
                return jsonify({"error": "Access forbidden"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator

# ------------- Limiter Key ----------------------
def get_user_id_for_limiter():
    """Returns user_id if logged in, otherwise IP"""
    from flask import request
    user = getattr(request, "user", None)
    if user and user.get("user_id"):
        return user.get("user_id")
    return request.remote_addr

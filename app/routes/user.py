from flask import Blueprint, request, jsonify
from app.services.user import (
    create_user,
    get_user_by_id,
    get_all_users,
    update_user,
    delete_user,
)
from app.services.auth import login, refresh, logout, reset_password, forgot_password
from app.utils.decorators import token_required, roles_allowed
from app.utils.helpers import rate_limit, response_formatter
from app.utils.logger import logger

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

# ============================================================
# 👤 USER CRUD ROUTES
# ============================================================

@user_bp.route("/", methods=["POST"])
@rate_limit("10 per hour")
@token_required
@roles_allowed("admin")
def create_user_route():
    """Register a new user (admin only)"""
    data = request.get_json()
    if not data:
        return jsonify(response_formatter(None, "No input data provided", False)), 400

    result, status_code = create_user(data)
    return jsonify(result), status_code


@user_bp.route("/", methods=["GET"])
@token_required
@roles_allowed("admin")
@rate_limit("30 per minute")
def get_all_users_route():
    """Admin can view all registered users"""
    result = get_all_users()  # Already returns response dict
    return jsonify(result), 200


@user_bp.route("/<string:user_id>", methods=["GET"])
@token_required
@rate_limit("60 per minute")
def get_user_route(user_id):
    """Fetch single user details (self or admin)"""
    current_user = request.user

    if current_user["user_id"] != user_id and current_user["role_name"].lower() != "admin":
        logger.warning(f"Unauthorized access attempt by {current_user['email']}")
        return jsonify(response_formatter(None, "Access forbidden", False)), 403

    result = get_user_by_id(user_id)  # Already returns response dict
    return jsonify(result), 200 if result["status"] else 404

@user_bp.route("/<string:user_id>", methods=["PUT"])
@token_required
@rate_limit("20 per minute")
def update_user_route(user_id):
    """Update user profile (self or admin)"""
    current_user = request.user
    data = request.get_json() or {}

    # Normal user can only update their own info
    if current_user["role_name"].lower() != "admin" and current_user["user_id"] != user_id:
        logger.warning(f"Unauthorized update attempt by {current_user['email']}")
        return jsonify({"status": False, "message": "Access forbidden"}), 403

    # Password update blocked
    if "password" in data:
        return jsonify({
            "status": False,
            "message": "Password cannot be updated here. Use /forgot-password or /reset-password."
        }), 400

    # Role update blocked for non-admin
    if "role_id" in data and current_user["role_name"].lower() != "admin":
        return jsonify({
            "status": False,
            "message": "You cannot update your role_id."
        }), 403

    result, status = update_user(user_id, data, current_user_role=current_user["role_name"])
    return jsonify(result), status

@user_bp.route("/<string:user_id>", methods=["DELETE"])
@token_required
@roles_allowed("admin")
@rate_limit("5 per minute")
def delete_user_route(user_id):
    """Delete user (Admin only)"""
    result = delete_user(user_id)  # Already returns response dict
    return jsonify(result), 200 if result["status"] else 404


# ============================================================
# 🔐 AUTHENTICATION ROUTES
# ============================================================

@user_bp.route("/login", methods=["POST"])
@rate_limit("5 per minute")
def login_route():
    """User login to get access and refresh tokens"""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(response_formatter(None, "Email and password required", False)), 400

    result, status = login(email, password)
    return jsonify(result), status


@user_bp.route("/forgot-password", methods=["POST"])
@rate_limit("3 per hour")
def forgot_password_route():
    data = request.get_json() or {}
    email = data.get("email")

    if not email:
        return jsonify(response_formatter(None, "Email is required", False)), 400

    result, status = forgot_password(email)
    return jsonify(result), status


@user_bp.route("/reset-password", methods=["POST"])
@rate_limit("3 per hour")
def reset_password_route():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify(response_formatter(None, "Token and new_password are required", False)), 400

    result, status = reset_password(token, new_password)
    return jsonify(result), status


@user_bp.route("/refresh", methods=["POST"])
@rate_limit("20 per minute")
def refresh_route():
    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify(response_formatter(None, "refresh_token required", False)), 400

    result, status = refresh(refresh_token)
    return jsonify(result), status


@user_bp.route("/logout", methods=["POST"])
@token_required
@rate_limit("20 per minute")
def logout_route():
    user_id = request.user["user_id"]
    result, status = logout(user_id)
    return jsonify(result), status

from flask import Blueprint, request, jsonify
from app.services.role import (
    create_role,
    get_all_roles,
    get_role_by_id,
    update_role,
    delete_role,
)
from app.utils.decorators import token_required, roles_allowed
from app.utils.helpers import rate_limit
from app.utils.logger import logger

# Blueprint setup
role_bp = Blueprint("role_bp", __name__, url_prefix="/roles")

# ============================================================
# 🔹 CREATE ROLE
# ============================================================
@role_bp.route("/", methods=["POST"])
@rate_limit("10 per hour")
def create_role_route():
    """Create a new role (admin only)"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    logger.info(f"Admin creating role: {data.get('role_name')}")
    result, status = create_role(data)
    return jsonify(result), status


# ============================================================
# 🔹 GET ALL ROLES
# ============================================================
@role_bp.route("/", methods=["GET"])
@token_required
@roles_allowed("admin")
@rate_limit("30 per minute")
def get_roles_route():
    """Get all roles (admin only)"""
    logger.info("Fetching all roles")
    result, status = get_all_roles()
    return jsonify(result), status


# ============================================================
# 🔹 GET ROLE BY ID
# ============================================================
@role_bp.route("/<string:role_id>", methods=["GET"])
@token_required
@roles_allowed("admin")
@rate_limit("60 per minute")
def get_role_route(role_id):
    """Get role details by ID (admin only)"""
    logger.info(f"Fetching role by ID: {role_id}")
    result, status = get_role_by_id(role_id)
    return jsonify(result), status


# ============================================================
# 🔹 UPDATE ROLE
# ============================================================
@role_bp.route("/<string:role_id>", methods=["PUT"])
@token_required
@roles_allowed("admin")
@rate_limit("20 per minute")
def update_role_route(role_id):
    """Update existing role name (admin only)"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    logger.info(f"Updating role ID: {role_id}")
    result, status = update_role(role_id, data)
    return jsonify(result), status


# ============================================================
# 🔹 DELETE ROLE
# ============================================================
@role_bp.route("/<string:role_id>", methods=["DELETE"])
@token_required
@roles_allowed("admin")
@rate_limit("5 per minute")
def delete_role_route(role_id):
    """Delete role (admin only)"""
    logger.info(f"Deleting role ID: {role_id}")
    result, status = delete_role(role_id)
    return jsonify(result), status

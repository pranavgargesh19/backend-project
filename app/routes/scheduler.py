# app/routes/manual_jobs.py
from flask import Blueprint, current_app, jsonify
from app.utils.decorators import token_required, roles_allowed
from app.services.scheduler import (
    deactivate_inactive_users,
    send_user_reports,
    backup_users_table
)

manual_bp = Blueprint('manual_bp', __name__, url_prefix='/manual')

# ------------------ Manual Scheduler Routes (Admin Only) ------------------

@manual_bp.route("/deactivate-users", methods=["POST"])
@token_required
@roles_allowed("admin")
def manual_deactivate_users():
    result = deactivate_inactive_users()
    return jsonify(result), 200

@manual_bp.route("/send-user-reports", methods=["POST"])
@token_required
@roles_allowed("admin") 
def manual_send_user_reports():
    send_user_reports(current_app)
    return jsonify({"status": "success", "message": "User reports sent"}), 200

@manual_bp.route("/backup-users", methods=["POST"])
@token_required
@roles_allowed("admin")  
def manual_backup_users():
    backup_users_table(current_app)
    return jsonify({"status": "success", "message": "Users table backed up"}), 200

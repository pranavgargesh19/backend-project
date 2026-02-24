# app/services/scheduler_jobs.py
from datetime import datetime, timedelta
from app.models.user import User, db
from app.utils.email import send_email_async
import os
import csv

# 1️⃣ Deactivate inactive users
from app.models.user import User
from app.db import db
from datetime import datetime, timedelta

def deactivate_inactive_users():
    """
    Deactivate users who haven't logged in for the last 30 days
    by updating their status to 'Inactive'.
    """
    threshold_date = datetime.utcnow() - timedelta(days=30)

    # Select users who are "Active" but haven't logged in recently
    inactive_users = User.query.filter(
        User.status == 'Active',
        User.last_login != None,  # Ignore users who never logged in (optional)
        User.last_login < threshold_date
    ).all()

    if not inactive_users:
        return {"status": "success", "message": "No inactive users to deactivate", "deactivated_users": []}

    deactivated_ids = []
    for user in inactive_users:
        user.status = 'Inactive'
        deactivated_ids.append(user.id)

    db.session.commit()

    return {"status": "success", "message": f"Deactivated {len(deactivated_ids)} users", "deactivated_users": deactivated_ids}

# 2️⃣ Send user activity reports to admins
def send_user_reports(app):
    with app.app_context():
        users = User.query.all()
        admins = User.query.filter(User.role_id.startswith("admin")).all()
        report = "\n".join([f"{u.id} - {u.email} - {u.status}" for u in users])
        for admin in admins:
            send_email_async(admin.email, "Daily User Report", report)
        app.logger.info(f"📬 Reports sent to {len(admins)} admin(s)")

# 4️⃣ Backup users table to CSV
def backup_users_table(app):
    with app.app_context():
        users = User.query.all()
        backup_folder = "backups"
        os.makedirs(backup_folder, exist_ok=True)
        filename = os.path.join(
            backup_folder,
            f"users_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "first_name", "middle_name", "last_name", "email", "phone", "role_id", "status", "last_login"])
            for u in users:
                writer.writerow([
                    u.id, u.first_name, getattr(u, "middle_name", ""), u.last_name,
                    u.email, u.phone, u.role_id, u.status,
                    getattr(u, "last_login", None)
                ])
        app.logger.info(f"💾 Users table backed up to {filename}")

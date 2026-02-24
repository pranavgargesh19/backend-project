# app/utils/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from datetime import datetime, timedelta
from app.models.user import User, db
from app.utils.email import send_email_async
import os
import csv
import atexit
import traceback

scheduler = BackgroundScheduler()


# ---------------- JOB FUNCTIONS ----------------

def deactivate_inactive_users(app):
    """Deactivate users who haven't logged in for more than 30 days."""
    with app.app_context():
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            users = User.query.filter(User.status == "Active").all()
            deactivated_count = 0
            for user in users:
                if hasattr(user, "last_login") and user.last_login and user.last_login < cutoff_date:
                    user.status = "Inactive"
                    deactivated_count += 1
            db.session.commit()
            app.logger.info(f"✅ Deactivated {deactivated_count} inactive users")
        except Exception as e:
            app.logger.error(f"⚠️ deactivate_inactive_users error: {e}")
            app.logger.error(traceback.format_exc())


def send_user_reports(app):
    """Send daily user activity reports to admins."""
    with app.app_context():
        try:
            users = User.query.all()
            admins = User.query.filter(User.role_id.startswith("admin")).all()
            report = "\n".join(
                [f"{u.id} - {u.email} - {u.status}" for u in users]
            )
            for admin in admins:
                send_email_async(admin.email, "Daily User Report", report)
            app.logger.info(f"📬 User reports sent to {len(admins)} admin(s)")
        except Exception as e:
            app.logger.error(f"⚠️ send_user_reports error: {e}")
            app.logger.error(traceback.format_exc())


def send_password_reminders(app):
    """Send reminders for password resets older than 24 hours."""
    with app.app_context():
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            users = User.query.filter(User.password_reset_requested_at != None).all()
            count = 0
            for user in users:
                if user.password_reset_requested_at and user.password_reset_requested_at < cutoff_time:
                    msg = f"Hi {user.first_name}, please reset your password if you haven't already."
                    send_email_async(user.email, "Password Reset Reminder", msg)
                    count += 1
            app.logger.info(f"⏰ Sent {count} password reset reminders")
        except Exception as e:
            app.logger.error(f"⚠️ send_password_reminders error: {e}")
            app.logger.error(traceback.format_exc())


def backup_users_table(app):
    """Backup the users table to CSV daily."""
    with app.app_context():
        try:
            users = User.query.all()
            backup_folder = "backups"
            os.makedirs(backup_folder, exist_ok=True)
            filename = os.path.join(
                backup_folder, f"users_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
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
        except Exception as e:
            app.logger.error(f"⚠️ backup_users_table error: {e}")
            app.logger.error(traceback.format_exc())


# ---------------- SCHEDULER SETUP ----------------

def start_scheduler(app):
    """
    Start APScheduler with all jobs.
    Use safe wrapper to catch exceptions and log them.
    """
    def safe_run(job_func):
        try:
            job_func(app)
        except Exception as e:
            app.logger.error(f"⚠️ Scheduler job {job_func.__name__} failed: {e}")
            app.logger.error(traceback.format_exc())

    # Job intervals (adjust seconds/minutes as needed)
    scheduler.add_job(lambda: safe_run(deactivate_inactive_users), 'interval', hours=24, id="deactivate_users")
    scheduler.add_job(lambda: safe_run(send_user_reports), 'interval', hours=24, id="send_reports")
    scheduler.add_job(lambda: safe_run(send_password_reminders), 'interval', hours=6, id="password_reminders")
    scheduler.add_job(lambda: safe_run(backup_users_table), 'interval', hours=24, id="backup_users")

    scheduler.start()
    app.logger.info("🕒 Scheduler started")

    # Shutdown scheduler on exit
    atexit.register(lambda: scheduler.shutdown())

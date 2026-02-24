from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User, db
from app.utils.jwt import create_access_token, create_refresh_token, decode_token, invalidate_token
from app.utils.email import send_email_async
from app.utils.helpers import is_valid_password
from flask import request
from app.utils.logger import logger

import uuid
from datetime import datetime, timedelta

# Temporary in-memory token store
reset_tokens = {}

# ----------------------------
# LOGIN
# ----------------------------
def login(email: str, password: str):
    ip = request.remote_addr
    logger.info(f"Login attempt for email: {email}, IP: {ip}")

    try:
        email = email.strip().lower()
        password = password.strip()

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            logger.warning(f"Failed login attempt for email: {email}, IP: {ip}")
            return {"error": "Invalid email or password"}, 401

        # ✅ Successful login: update last_login
        user.last_login = datetime.utcnow()
        db.session.commit()

        logger.info(f"Successful login for user_id: {user.id}, IP: {ip}")

        # ✅ Include role_name in token identity
        role_name = user.role.role_name if user.role else "user"

        identity = {
            "user_id": user.id,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": role_name
        }

        access_token = create_access_token(identity)
        refresh_token = create_refresh_token(identity)

        user_info = {
            "id": user.id,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "salutation": user.salutation,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else None,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": role_name,  # ✅ Added
            "status": user.status,
            "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S")
        }

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_info
        }, 200

    except Exception as e:
        logger.error(f"Login error for email {email}: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


# ----------------------------
# REFRESH TOKEN
# ----------------------------
def refresh(refresh_token: str):
    try:
        ok, payload_or_err = decode_token(refresh_token)
        if not ok:
            logger.warning(f"Invalid refresh token attempt: {payload_or_err}")
            return {"error": payload_or_err}, 401

        payload = payload_or_err
        if payload.get("type") != "refresh":
            logger.warning(f"Token is not a refresh token: {payload}")
            return {"error": "Token is not a refresh token"}, 401

        user_id = payload.get("sub")
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"Refresh token used for non-existent user_id: {user_id}")
            return {"error": "User not found"}, 404

        # ✅ Load role_name dynamically
        role_name = user.role.role_name if user.role else "user"

        identity = {
            "user_id": user.id,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": role_name
        }

        new_access = create_access_token(identity)
        new_refresh = create_refresh_token(identity)

        logger.info(f"Refresh token issued for user_id: {user.id}")

        return {"access_token": new_access, "refresh_token": new_refresh}, 200
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        return {"error": "Internal server error"}, 500


# ----------------------------
# LOGOUT
# ----------------------------
def logout(user_id):
    from flask import request

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"status": False, "message": "Missing token"}, 400

    token = auth_header.split(" ")[1]
    invalidate_token(token)

    return {"status": True, "message": "Successfully logged out"}, 200


# ----------------------------
# FORGOT PASSWORD
# ----------------------------
def forgot_password(email: str):
    user = User.query.filter_by(email=email).first()
    if not user:
        logger.warning(f"Forgot password attempt for non-existent email: {email}")
        return {"error": "Email does not exist"}, 404

    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=1)
    reset_tokens[token] = {"user_id": user.id, "expires": expires}

    reset_link = f"http://localhost:5000/users/reset-password?token={token}"
    subject = "Reset Your Password"
    body = f"""
Hi {user.first_name or 'User'},

We received a request to reset your password.
Click the link below to reset it:

{reset_link}

This link will expire in 1 hour.
If you didn’t request this, please ignore this email.

Regards,
Your App Team
"""

    try:
        send_email_async(user.email, subject, body)
        logger.info(f"Password reset link sent for email: {email}")
        return {"message": "Password reset link sent successfully to your email."}, 200
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {str(e)}")
        return {"error": "Failed to send reset email. Please try again later."}, 500


# ----------------------------
# RESET PASSWORD
# ----------------------------
def reset_password(token: str, new_password: str):
    data = reset_tokens.get(token)
    if not data:
        logger.warning(f"Invalid or expired password reset token: {token}")
        return {"error": "Invalid or expired token"}, 400

    if data["expires"] < datetime.utcnow():
        del reset_tokens[token]
        logger.warning(f"Expired password reset token used: {token}")
        return {"error": "Token expired"}, 400

    user = User.query.get(data["user_id"])
    if not user:
        logger.warning(f"Password reset attempted for non-existent user_id: {data['user_id']}")
        return {"error": "User not found"}, 404

    valid, message = is_valid_password(new_password)
    if not valid:
        logger.warning(f"Password reset validation failed for user_id: {user.id}")
        return {"error": message}, 400

    try:
        user.password = generate_password_hash(new_password)
        db.session.add(user)
        db.session.commit()
        logger.info(f"Password reset successfully for user_id: {user.id}")
        del reset_tokens[token]
        return {"message": "Password reset successfully"}, 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset error for user_id {user.id}: {str(e)}")
        return {"error": "Internal server error"}, 500

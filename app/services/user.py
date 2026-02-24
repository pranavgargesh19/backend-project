import re
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from app.models.user import User, db
from app.utils.helpers import validate_user_data, format_user, response_formatter
from app.utils.logger import logger

# ---------------- Create User ----------------
def create_user(data):
    logger.info(f"Attempting to create user with email: {data.get('email')}")
    
    # Validate input
    is_valid, message = validate_user_data(data)
    if not is_valid:
        logger.warning(f"User creation failed validation: {message}")
        return response_formatter(None, message, False), 400

    raw_password = data.get('password')
    if not raw_password:
        logger.warning(f"User creation failed: password not provided for email {data.get('email')}")
        return response_formatter(None, "Password is required", False), 400

    hashed_password = generate_password_hash(raw_password)

    new_user = User(
        first_name=data['first_name'],
        middle_name=data.get('middle_name'),
        last_name=data['last_name'],
        salutation=data.get('salutation'),
        gender=data.get('gender'),
        date_of_birth=data.get('date_of_birth'),
        email=data['email'],
        phone=data.get('phone'),
        role_id=data.get('role_id'),
        status=data.get('status', 'Active'),
        password=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User created successfully: user_id {new_user.id}, email {new_user.email}")
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database error on create_user: {str(e.orig)}")
        if "Duplicate entry" in str(e.orig) and "users.email" in str(e.orig):
            return response_formatter(None, "Email already exists. Please use a different email.", False), 400
        return response_formatter(None, f"Database error: {str(e.orig)}", False), 500

    return response_formatter(format_user(new_user), "User created successfully"), 201

# ---------------- Get All Users ----------------
def get_all_users():
    logger.info("Fetching all users")
    users = User.query.all()
    serialized_users = [format_user(u) for u in users]
    return response_formatter(serialized_users, "All users retrieved")

# ---------------- Get User By ID ----------------
def get_user_by_id(user_id):
    logger.info(f"Fetching user by id: {user_id}")
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"User not found: user_id {user_id}")
        return response_formatter(None, "User not found", False), 404
    return response_formatter(format_user(user), "User retrieved successfully")

# ---------------- Update User ----------------
def update_user(user_id, data, current_user_role="user"):
    """Update user info with role & password restrictions"""
    user = User.query.get(user_id)
    if not user:
        return response_formatter(None, "User not found", False), 404

    # Validate fields
    is_valid, message = validate_user_data(data, update=True)
    if not is_valid:
        return response_formatter(None, message, False), 400

    # Update allowed fields for all
    for key in ["first_name", "middle_name", "last_name", "salutation", "gender", "status"]:
        if key in data and data[key] is not None:
            setattr(user, key, data[key])

    # Only admin can update role_id
    if "role_id" in data and current_user_role.lower() == "admin":
        user.role_id = data["role_id"]

    # Update date_of_birth
    if "date_of_birth" in data and data["date_of_birth"]:
        try:
            if isinstance(data["date_of_birth"], str):
                user.date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
            else:
                user.date_of_birth = data["date_of_birth"]
        except ValueError:
            return response_formatter(None, "Invalid date_of_birth format. Use YYYY-MM-DD.", False), 400

    try:
        db.session.commit()
        db.session.refresh(user)
    except Exception as e:
        db.session.rollback()
        return response_formatter(None, f"Database error: {str(e)}", False), 500

    return response_formatter(format_user(user), "User updated successfully"), 200

# ---------------- Delete User ----------------
def delete_user(user_id):
    logger.info(f"Deleting user_id: {user_id}")
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"Delete failed: user not found {user_id}")
        return response_formatter(None, "User not found", False), 404
    db.session.delete(user)
    db.session.commit()
    logger.info(f"User deleted successfully: user_id {user_id}")
    return response_formatter(None, "User deleted successfully")

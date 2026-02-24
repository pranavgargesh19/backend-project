# app/utils/helper.py
import re
from flask import current_app
from app.models.user import User, db
from app.models.role import Role

ALLOWED_SALUTATIONS = ['Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Prof.']
ALLOWED_GENDERS = ['Male', 'Female', 'Other', 'Prefer not to say']
ALLOWED_STATUSES = [
    'Active', 'Inactive', 'Interview Scheduled', 'Onboarding',
    'KYC Pending', 'Under Review', 'Terminated'
]

def is_valid_email(email):
    pattern = r'^[A-Za-z0-9]+([._-]?[A-Za-z0-9]+)*@[A-Za-z0-9-]+(\.[A-Za-z]{2,6})+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def is_valid_password(password):
    """
    Validates password strength:
    - At least 8 characters long
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""

def validate_user_data(data, update=False):
    """
    Validates user data before creating or updating.
    Returns (is_valid: bool, error_message: str)
    """
    # Salutation
    if 'salutation' in data and data['salutation'] not in ALLOWED_SALUTATIONS:
        return False, f"Invalid salutation. Allowed: {ALLOWED_SALUTATIONS}"
    
    # Gender
    if 'gender' in data and data['gender'] not in ALLOWED_GENDERS:
        return False, f"Invalid gender. Allowed: {ALLOWED_GENDERS}"
    
    # Status
    if 'status' in data and data['status'] not in ALLOWED_STATUSES:
        return False, f"Invalid status. Allowed: {ALLOWED_STATUSES}"
    
    # Email
    if 'email' in data:
        if not is_valid_email(data['email']):
            return False, "Invalid email format"
        if not update and User.query.filter_by(email=data['email']).first():
            return False, "Email already exists"
    
    # Phone
    if 'phone' in data and data['phone']:
        phone = data['phone']
        if not phone.isdigit():
            return False, "Phone number must contain only digits"
        if len(phone) != 10:
            return False, "Phone number must be exactly 10 digits"
        if phone[0] not in '6789':
            return False, "Phone number must start with 6, 7, 8, or 9"

    # Password (only validate on create or if explicitly updating password)
    if not update or ('password' in data and data['password']):
        password = data.get('password')
        if not password:
            return False, "Password is required"
        valid_pass, msg = is_valid_password(password)
        if not valid_pass:
            return False, msg

    return True, ""

def format_user(user):
    """
    Converts SQLAlchemy model object to dict and formats date fields,
    excluding sensitive fields like password.
    """
    data = {
        "id": user.id,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "salutation": user.salutation,
        "gender": user.gender,
        "date_of_birth": user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
        "email": user.email,
        "phone": user.phone,
        "role_id": user.role_id,
        "status": user.status
    }
    return data

def response_formatter(data=None, message="", status=True):
    """
    Standardized API response structure.
    """
    return {
        "status": status,
        "message": message,
        "data": data
    }

# ----------------- Helper -----------------
def rate_limit(limit: str):
    """Fetch current limiter at runtime"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def wrapper(*args, **kwargs):
            limiter = current_app.limiter  # access limiter inside app context
            return limiter.limit(limit)(f)(*args, **kwargs)
        return wrapper
    return decorator

def serialize_user(user):
    """Return user dict including role_name"""
    return {
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
        "role_name": getattr(user.role, "name", None) , # <-- Add role name
        "status": user.status,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
    }


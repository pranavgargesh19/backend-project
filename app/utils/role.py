# app/utils/role_utils.py

def is_admin(role_name: str) -> bool:
    """Return True if the given role_name is admin."""
    return role_name and role_name.lower() == "admin"

def is_user(role_name: str) -> bool:
    """Return True if the given role_name is user."""
    return role_name and role_name.lower() == "user"

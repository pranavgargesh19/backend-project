import jwt
from datetime import datetime, timedelta
from flask import current_app, request

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRES_DAYS = 7

# ✅ In-memory blacklist for invalidated tokens
TOKEN_BLACKLIST = set()

def create_access_token(identity: dict):
    now = datetime.utcnow()
    payload = {
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
        "type": "access",
        "sub": identity["user_id"],
        "data": identity
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm=ALGORITHM)
    return token

def create_refresh_token(identity: dict):
    now = datetime.utcnow()
    payload = {
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        "type": "refresh",
        "sub": identity["user_id"]
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm=ALGORITHM)
    return token

def decode_token(token: str):
    # ✅ Check blacklist before decoding
    if token in TOKEN_BLACKLIST:
        return False, "Token invalidated. Please log in again."

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=[ALGORITHM])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidTokenError as e:
        return False, f"Invalid token: {str(e)}"

def create_reset_token(user_id: str, expires_in_minutes: int = 15):
    payload = {
        "sub": user_id,
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token

def decode_reset_token(token: str):
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        if payload.get("type") != "reset":
            return False, "Invalid token type"
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"

# ✅ Function to invalidate current token on logout
def invalidate_token(token: str):
    TOKEN_BLACKLIST.add(token)

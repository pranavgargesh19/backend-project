# test_scheduler.py
from datetime import datetime, timedelta
from app.services.auth import reset_tokens

# Add an expired token
reset_tokens['test-token-expired'] = {
    "user_id": "user-001",
    "expires": datetime.utcnow() - timedelta(minutes=1)  # already expired
}

# Add a valid token
reset_tokens['test-token-valid'] = {
    "user_id": "user-002",
    "expires": datetime.utcnow() + timedelta(minutes=5)
}

print("Before scheduler:", reset_tokens)

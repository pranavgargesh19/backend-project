# app/models/user.py
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum, Date
from app.db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    salutation = db.Column(db.Enum('Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Prof.'), nullable=True)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', 'Prefer not to say'), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    role_id = db.Column(db.String(36), db.ForeignKey("roles.id"), nullable=True)
    status = db.Column(
        db.Enum('Active', 'Inactive', 'Interview Scheduled', 'Onboarding',
                'KYC Pending', 'Under Review', 'Terminated'),
        nullable=True,
        default='Active'
    )
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)


    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

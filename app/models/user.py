from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' | 'company' | 'student'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship(
        "StudentProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    company_profile = db.relationship(
        "CompanyProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "is_blacklisted": self.is_blacklisted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    branch = db.Column(db.String(80))
    year = db.Column(db.Integer)  # graduation year
    cgpa = db.Column(db.Float)
    phone = db.Column(db.String(20))
    resume_filename = db.Column(db.String(255))

    applications = db.relationship(
        "Application", backref="student", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "branch": self.branch,
            "year": self.year,
            "cgpa": self.cgpa,
            "phone": self.phone,
            "resume_filename": self.resume_filename,
        }


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(80))
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default="pending")  # pending/approved/rejected

    drives = db.relationship("Drive", backref="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "hr_contact": self.hr_contact,
            "website": self.website,
            "approval_status": self.approval_status,
        }

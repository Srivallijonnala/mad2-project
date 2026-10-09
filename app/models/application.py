from datetime import datetime
from app.extensions import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drives.id"), nullable=False)

    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="applied")  # applied/shortlisted/selected/rejected

    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uix_student_drive"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "drive_id": self.drive_id,
            "job_title": self.drive.job_title if self.drive else None,
            "company_name": self.drive.company.company_name if self.drive and self.drive.company else None,
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "status": self.status,
        }

from datetime import datetime
from app.extensions import db


class Drive(db.Model):
    __tablename__ = "drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)

    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)

    # Eligibility criteria
    eligible_branches = db.Column(db.String(255))  # comma separated e.g. "CSE,ECE"
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_year = db.Column(db.Integer)  # graduation year eligible

    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending/approved/rejected/closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship(
        "Application", backref="drive", cascade="all, delete-orphan"
    )

    def to_dict(self, include_company=True):
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "eligible_branches": self.eligible_branches,
            "min_cgpa": self.min_cgpa,
            "eligible_year": self.eligible_year,
            "application_deadline": self.application_deadline.isoformat()
            if self.application_deadline else None,
            "status": self.status,
            "applicant_count": len(self.applications),
        }
        if include_company and self.company:
            data["company_name"] = self.company.company_name
        return data

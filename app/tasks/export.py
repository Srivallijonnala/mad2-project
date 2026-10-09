import csv
import io
import os
import uuid

from app.tasks.celery_app import celery_app
from app.models import Application
from app.utils.notify import send_email

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


@celery_app.task(name="app.tasks.export.export_applications_csv")
def export_applications_csv(student_profile_id: int, student_email: str, student_name: str):
    """Async job: build a CSV of the student's application history and email an alert
    once it's done. Returns the server-side file path + filename in the task result."""
    applications = Application.query.filter_by(student_id=student_profile_id).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Student ID", "Company Name", "Drive Title", "Application Status", "Application Date"])
    for a in applications:
        writer.writerow([
            student_profile_id,
            a.drive.company.company_name if a.drive and a.drive.company else "",
            a.drive.job_title if a.drive else "",
            a.status,
            a.application_date.isoformat() if a.application_date else "",
        ])

    filename = f"applications_{student_profile_id}_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, "w", newline="") as f:
        f.write(buffer.getvalue())

    send_email(
        student_email,
        "Your Placement Application Export is Ready",
        f"<p>Hi {student_name},</p><p>Your application history export ({len(applications)} "
        f"records) has completed and is ready on the server: {filename}</p>",
    )

    return {"filename": filename, "records": len(applications)}

from datetime import datetime, timedelta

from app.tasks.celery_app import celery_app
from app.models import Drive, Application, StudentProfile
from app.utils.notify import send_gchat_message, send_email


@celery_app.task(name="app.tasks.reminders.send_daily_reminders")
def send_daily_reminders():
    """Runs daily. Notifies students with drives whose deadline is within the next 3 days
    that they haven't applied to yet."""
    now = datetime.utcnow()
    soon = now + timedelta(days=3)

    upcoming_drives = Drive.query.filter(
        Drive.status == "approved",
        Drive.application_deadline >= now,
        Drive.application_deadline <= soon,
    ).all()

    if not upcoming_drives:
        send_gchat_message("Daily reminder job ran: no upcoming deadlines in the next 3 days.")
        return {"notified": 0, "drives_checked": 0}

    notified = 0
    students = StudentProfile.query.all()
    applied_pairs = {(a.student_id, a.drive_id) for a in Application.query.all()}

    for student in students:
        pending_drives = [
            d for d in upcoming_drives if (student.id, d.id) not in applied_pairs
        ]
        if not pending_drives:
            continue

        titles = ", ".join(f"{d.job_title} (due {d.application_deadline:%d-%b})" for d in pending_drives)
        message = f"Reminder for {student.user.name}: pending applications - {titles}"
        send_gchat_message(message)
        send_email(
            student.user.email,
            "Placement Portal - Upcoming Application Deadlines",
            f"<p>Hi {student.user.name},</p><p>You have pending applications: {titles}</p>",
        )
        notified += 1

    return {"notified": notified, "drives_checked": len(upcoming_drives)}

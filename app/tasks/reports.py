from datetime import datetime, timedelta

from app.tasks.celery_app import celery_app
from app.config import Config
from app.models import Drive, Application, StudentProfile
from app.utils.notify import send_email


@celery_app.task(name="app.tasks.reports.generate_monthly_report")
def generate_monthly_report():
    """Runs on the 1st of every month. Builds an HTML activity report and emails it
    to the institute admin."""
    now = datetime.utcnow()
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)

    drives_last_month = Drive.query.filter(
        Drive.created_at >= first_of_last_month, Drive.created_at < first_of_this_month
    ).all()
    applications_last_month = Application.query.filter(
        Application.application_date >= first_of_last_month,
        Application.application_date < first_of_this_month,
    ).all()
    selected_last_month = [a for a in applications_last_month if a.status == "selected"]

    html = f"""
    <h2>Placement Portal — Monthly Activity Report</h2>
    <p>Period: {first_of_last_month:%B %Y}</p>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Drives conducted</td><td>{len(drives_last_month)}</td></tr>
        <tr><td>Students applied</td><td>{len(applications_last_month)}</td></tr>
        <tr><td>Students selected</td><td>{len(selected_last_month)}</td></tr>
        <tr><td>Total registered students</td><td>{StudentProfile.query.count()}</td></tr>
    </table>
    <h3>Drives</h3>
    <ul>
        {''.join(f"<li>{d.job_title} — {d.company.company_name} ({d.status})</li>" for d in drives_last_month) or '<li>None</li>'}
    </ul>
    """

    send_email(Config.ADMIN_EMAIL, f"Monthly Placement Report - {first_of_last_month:%B %Y}", html)
    return {
        "drives": len(drives_last_month),
        "applications": len(applications_last_month),
        "selected": len(selected_last_month),
    }

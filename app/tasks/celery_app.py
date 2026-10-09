from celery import Celery
from celery.schedules import crontab

from app import create_app
from app.config import Config

flask_app = create_app()

celery_app = Celery(
    "ppa",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=["app.tasks.reminders", "app.tasks.reports", "app.tasks.export"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Scheduled (beat) jobs
celery_app.conf.beat_schedule = {
    "daily-deadline-reminders": {
        "task": "app.tasks.reminders.send_daily_reminders",
        "schedule": crontab(hour=9, minute=0),  # every day at 09:00 UTC
    },
    "monthly-activity-report": {
        "task": "app.tasks.reports.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),  # 1st of month, 06:00 UTC
    },
}


class ContextTask(celery_app.Task):
    """Ensure every task runs inside a Flask application context (needed for db access)."""
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = ContextTask

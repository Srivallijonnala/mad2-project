"""
Run the Celery beat scheduler (triggers the daily reminder & monthly report jobs):
    celery -A celery_worker.celery_app beat --loglevel=info
"""

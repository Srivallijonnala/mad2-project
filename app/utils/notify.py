import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from flask import current_app


def send_gchat_message(text: str):
    """Post a message to a Google Chat incoming webhook. Falls back to console log
    if no webhook is configured, so the batch job still runs locally without setup."""
    webhook_url = current_app.config.get("GCHAT_WEBHOOK_URL")
    if not webhook_url:
        print(f"[GCHAT-SIM] {text}")
        return True
    try:
        resp = requests.post(webhook_url, json={"text": text}, timeout=10)
        return resp.status_code == 200
    except requests.RequestException as exc:
        print(f"[GCHAT-ERROR] {exc}")
        return False


def send_email(to_email: str, subject: str, html_body: str):
    """Send an email via SMTP. Falls back to console log if SMTP is not configured,
    so monthly reports / exports still 'complete' during local demos."""
    host = current_app.config.get("SMTP_HOST")
    user = current_app.config.get("SMTP_USER")
    password = current_app.config.get("SMTP_PASSWORD")
    port = current_app.config.get("SMTP_PORT")

    if not host or not user:
        print(f"[EMAIL-SIM] To: {to_email} | Subject: {subject}\n{html_body[:500]}")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, to_email, msg.as_string())
        return True
    except Exception as exc:
        print(f"[EMAIL-ERROR] {exc}")
        return False

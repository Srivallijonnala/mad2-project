# Placement Portal Application (PPA)

A multi-role campus recruitment platform that replaces spreadsheet- and email-based coordination between an institute, companies, and students. Built with a **Flask REST API**, a **Vue 3** single-page front end, and **Celery + Redis** for background jobs and caching.

Developed as the **MAD 2 (Modern Application Development 2)** project for the IIT Madras BS Degree Program.

---

## Overview

PPA supports three roles, each with a dedicated dashboard:

- **Admin (Institute Placement Cell)**: approves companies and drives, manages users, and monitors the platform
- **Company**: registers, creates placement drives, and shortlists or selects applicants
- **Student**: builds a profile, uploads a resume, applies to eligible drives, and tracks applications

The app covers the full placement lifecycle: **company onboarding, drive creation and approval, student applications, shortlisting, and final selection**. Company registrations and drive creation go through an admin approval step, matching the real-world workflow.

---

## Key Features

- **Role-based access control** with session-based authentication
- **Admin approval workflow** for companies and placement drives
- **Blacklisting and deactivation** of companies and students
- **Eligibility checks** on applications (branch, minimum CGPA, year) with duplicate-application prevention
- **Resume upload** (PDF/DOC/DOCX) and searchable drive listings
- **Redis caching** for read-heavy endpoints, invalidated on admin or company changes
- **Three Celery background jobs**:
  - **Daily reminder** (09:00 UTC): notifies students who haven't applied to drives with deadlines in the next 3 days, by email and Google Chat webhook
  - **Monthly activity report** (1st of each month, 06:00 UTC): emails the admin an HTML summary of drives, applications, and selections
  - **CSV export** (on demand): students export their application history asynchronously and can poll the task status
- **Graceful fallbacks**: email and webhook notifications log to the console when not configured, so everything runs in a local demo

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Flask 3.x, Flask-SQLAlchemy |
| Frontend | Vue 3 (CDN, ES modules), Bootstrap 5 |
| Database | SQLite |
| Cache | Redis, Flask-Caching |
| Task queue | Celery 5 with Redis broker and backend |
| Notifications | SMTP email, Google Chat webhook |
| Templating | Jinja2 (single HTML entry point only) |

---

## Database Design

Five models: **User**, **StudentProfile**, **CompanyProfile**, **Drive**, and **Application**.

- User to StudentProfile / CompanyProfile: one-to-one, depending on role
- CompanyProfile to Drive: one-to-many
- StudentProfile to Application: one-to-many
- Drive to Application: one-to-many
- Unique constraint on `(student_id, drive_id)` so a student can apply to a drive only once

Tables are created programmatically with `db.create_all()`. The single admin account is seeded by `create_db.py`; there is no admin registration route.

---

## Project Structure

```
├── app/
│   ├── __init__.py        # Flask application factory
│   ├── config.py          # Configuration (DB, Redis, Celery, SMTP, webhook)
│   ├── extensions.py      # Shared extensions (cache)
│   ├── models/            # User, StudentProfile, CompanyProfile, Drive, Application
│   ├── routes/            # Blueprints: auth, admin, company, student, pages
│   ├── tasks/             # Celery app, beat schedule, and background jobs
│   ├── utils/             # Decorators (login/role checks), notification helpers
│   ├── static/js/         # Vue app: router, API client, components, pages
│   └── templates/
│       └── index.html     # The only Jinja2 template (SPA shell)
├── create_db.py           # Creates tables and seeds the admin user
├── celery_worker.py       # Celery worker entry point
├── celery_beat.py         # Celery beat scheduler entry point
└── requirements.txt
```

---

## API Overview

| Area | Examples |
|---|---|
| Auth | `POST /api/auth/register/student`, `POST /api/auth/login`, `GET /api/auth/me` |
| Student | `GET /api/student/drives`, `POST /api/student/drives/<id>/apply`, `POST /api/student/export` |
| Company | `POST /api/company/drives`, `GET /api/company/drives/<id>/applications`, `PUT /api/company/applications/<id>/status` |
| Admin | `GET /api/admin/stats`, `POST /api/admin/companies/<id>/approve`, `POST /api/admin/drives/<id>/approve` |

---

## Getting Started

**Prerequisites:** Python 3.10+ and a running Redis server.

1. **Clone the repository and open the project folder**

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Create the database and seed the admin user**
   ```
   python create_db.py
   ```

5. **Start Redis**, then run the Flask app
   ```
   flask --app app run
   ```

6. **Start the Celery worker and scheduler** (in separate terminals)
   ```
   celery -A celery_worker worker --loglevel=info --pool=solo
   celery -A celery_beat beat --loglevel=info
   ```

7. Open `http://127.0.0.1:5000` in your browser.

Admin credentials are set in `app/config.py`. Optional SMTP and Google Chat webhook settings are also configured there.



---

## AI / LLM Declaration

Claude.ai was used to improve documentation wording and clarify certain backend concepts. ChatGPT-5 was used to generate basic frontend button and div code, which was reviewed and integrated manually. The core implementation, database design, debugging, and system integration were done independently by the author.

---

## Author

**Srivalli Jonnala**
Standalone student, IIT Madras BS Degree Program

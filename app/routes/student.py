import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from app.extensions import db, cache
from app.models import Drive, Application
from app.utils.decorators import role_required, get_current_user

student_bp = Blueprint("student", __name__, url_prefix="/api/student")

ALLOWED_RESUME_EXT = {"pdf", "doc", "docx"}


@student_bp.route("/profile", methods=["GET"])
@role_required("student")
def get_profile():
    user = get_current_user()
    return jsonify(user.student_profile.to_dict())


@student_bp.route("/profile", methods=["PUT"])
@role_required("student")
def update_profile():
    user = get_current_user()
    data = request.get_json(force=True) or {}
    profile = user.student_profile
    profile.branch = data.get("branch", profile.branch)
    profile.year = data.get("year", profile.year)
    profile.cgpa = data.get("cgpa", profile.cgpa)
    profile.phone = data.get("phone", profile.phone)
    db.session.commit()
    return jsonify(profile.to_dict())


@student_bp.route("/resume", methods=["POST"])
@role_required("student")
def upload_resume():
    user = get_current_user()
    if "resume" not in request.files:
        return jsonify({"error": "No file part 'resume'"}), 400
    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_RESUME_EXT:
        return jsonify({"error": "Only pdf/doc/docx files are allowed"}), 400

    filename = f"{uuid.uuid4().hex}_{user.id}.{ext}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    user.student_profile.resume_filename = filename
    db.session.commit()
    return jsonify({"message": "Resume uploaded", "resume_filename": filename})


@student_bp.route("/drives", methods=["GET"])
@role_required("student")
@cache.cached(timeout=30, query_string=True)
def list_approved_drives():
    """Approved & not-yet-closed drives, optionally filtered by branch/search."""
    q = request.args.get("q", "").strip()
    branch = request.args.get("branch", "").strip()

    query = Drive.query.filter_by(status="approved")
    if q:
        query = query.filter(Drive.job_title.ilike(f"%{q}%"))
    if branch:
        query = query.filter(Drive.eligible_branches.ilike(f"%{branch}%"))

    drives = query.order_by(Drive.application_deadline.asc()).all()
    return jsonify([d.to_dict() for d in drives])


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_drive(drive_id):
    user = get_current_user()
    student = user.student_profile
    drive = Drive.query.get_or_404(drive_id)

    if drive.status != "approved":
        return jsonify({"error": "This drive is not open for applications"}), 400

    from datetime import datetime
    if drive.application_deadline < datetime.utcnow():
        return jsonify({"error": "Application deadline has passed"}), 400

    # Eligibility validation
    if drive.min_cgpa and (student.cgpa or 0) < drive.min_cgpa:
        return jsonify({"error": f"Minimum CGPA required: {drive.min_cgpa}"}), 400
    if drive.eligible_branches:
        eligible = [b.strip().lower() for b in drive.eligible_branches.split(",")]
        if (student.branch or "").lower() not in eligible:
            return jsonify({"error": "Your branch is not eligible for this drive"}), 400
    if drive.eligible_year and student.year and student.year != drive.eligible_year:
        return jsonify({"error": f"Only students graduating in {drive.eligible_year} are eligible"}), 400

    # Prevent duplicate applications
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        return jsonify({"error": "You have already applied to this drive"}), 409

    application = Application(student_id=student.id, drive_id=drive_id, status="applied")
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application submitted", "application": application.to_dict()}), 201


@student_bp.route("/applications", methods=["GET"])
@role_required("student")
def my_applications():
    user = get_current_user()
    apps = Application.query.filter_by(student_id=user.student_profile.id).order_by(
        Application.application_date.desc()
    ).all()
    return jsonify([a.to_dict() for a in apps])


@student_bp.route("/export", methods=["POST"])
@role_required("student")
def export_applications():
    """Trigger an async Celery job to export the student's application history as CSV."""
    user = get_current_user()
    from app.tasks.export import export_applications_csv
    task = export_applications_csv.delay(user.student_profile.id, user.email, user.name)
    return jsonify({
        "message": "Export started. You'll be notified once it's ready.",
        "task_id": task.id,
    }), 202


@student_bp.route("/export/status/<task_id>", methods=["GET"])
@role_required("student")
def export_status(task_id):
    from app.tasks.celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    payload = {"task_id": task_id, "state": result.state}
    if result.state == "SUCCESS":
        payload["result"] = result.result
    elif result.state == "FAILURE":
        payload["error"] = str(result.result)
    return jsonify(payload)

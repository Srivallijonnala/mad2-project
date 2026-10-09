from datetime import datetime
from flask import Blueprint, request, jsonify

from app.extensions import db, cache
from app.models import Drive, Application, StudentProfile
from app.utils.decorators import role_required, get_current_user

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


@company_bp.route("/profile", methods=["GET"])
@role_required("company")
def get_profile():
    user = get_current_user()
    return jsonify(user.company_profile.to_dict())


@company_bp.route("/profile", methods=["PUT"])
@role_required("company")
def update_profile():
    user = get_current_user()
    data = request.get_json(force=True) or {}
    profile = user.company_profile
    profile.hr_contact = data.get("hr_contact", profile.hr_contact)
    profile.website = data.get("website", profile.website)
    db.session.commit()
    return jsonify(profile.to_dict())


@company_bp.route("/drives", methods=["GET"])
@role_required("company")
def list_my_drives():
    user = get_current_user()
    drives = Drive.query.filter_by(company_id=user.company_profile.id).order_by(
        Drive.created_at.desc()
    ).all()
    return jsonify([d.to_dict(include_company=False) for d in drives])


@company_bp.route("/drives", methods=["POST"])
@role_required("company")
def create_drive():
    user = get_current_user()
    data = request.get_json(force=True) or {}

    required = ["job_title", "application_deadline"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "job_title and application_deadline are required"}), 400

    try:
        deadline = datetime.fromisoformat(data["application_deadline"])
    except ValueError:
        return jsonify({"error": "application_deadline must be an ISO date/datetime"}), 400

    drive = Drive(
        company_id=user.company_profile.id,
        job_title=data["job_title"],
        job_description=data.get("job_description", ""),
        eligible_branches=data.get("eligible_branches", ""),
        min_cgpa=data.get("min_cgpa", 0.0),
        eligible_year=data.get("eligible_year"),
        application_deadline=deadline,
        status="pending",  # requires admin approval
    )
    db.session.add(drive)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Drive created, pending admin approval", "drive": drive.to_dict()}), 201


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@role_required("company")
def drive_applications(drive_id):
    user = get_current_user()
    drive = Drive.query.get_or_404(drive_id)
    if drive.company_id != user.company_profile.id:
        return jsonify({"error": "Forbidden"}), 403

    apps = Application.query.filter_by(drive_id=drive_id).all()
    result = []
    for a in apps:
        d = a.to_dict()
        d["student_name"] = a.student.user.name
        d["student_email"] = a.student.user.email
        d["cgpa"] = a.student.cgpa
        d["branch"] = a.student.branch
        d["resume_filename"] = a.student.resume_filename
        result.append(d)
    return jsonify(result)


@company_bp.route("/applications/<int:application_id>/status", methods=["PUT"])
@role_required("company")
def update_application_status(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != user.company_profile.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("applied", "shortlisted", "selected", "rejected"):
        return jsonify({"error": "Invalid status"}), 400

    application.status = new_status
    db.session.commit()
    return jsonify({"message": "Application status updated", "application": application.to_dict()})

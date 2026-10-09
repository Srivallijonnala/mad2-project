from flask import Blueprint, request, jsonify

from app.extensions import db, cache
from app.models import User, StudentProfile, CompanyProfile, Drive, Application
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=30, query_string=True)  
def stats():
    return jsonify({
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.filter_by(approval_status="approved").count(),
        "total_drives": Drive.query.count(),
        "pending_company_approvals": CompanyProfile.query.filter_by(approval_status="pending").count(),
        "pending_drive_approvals": Drive.query.filter_by(status="pending").count(),
        "total_applications": Application.query.count(),
        "total_selected": Application.query.filter_by(status="selected").count(),
    })


@admin_bp.route("/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    q = request.args.get("q", "").strip()
    query = CompanyProfile.query
    if q:
        query = query.filter(CompanyProfile.company_name.ilike(f"%{q}%"))
    companies = query.all()
    result = []
    for c in companies:
        d = c.to_dict()
        d["user"] = c.user.to_dict()
        result.append(d)
    return jsonify(result)


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@role_required("admin")
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Company approved", "company": company.to_dict()})


@admin_bp.route("/companies/<int:company_id>/reject", methods=["POST"])
@role_required("admin")
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Company rejected", "company": company.to_dict()})


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["POST"])
@role_required("admin")
def blacklist_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.user.is_blacklisted = not company.user.is_blacklisted
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Company blacklist toggled", "company": company.to_dict()})


@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def list_students():
    q = request.args.get("q", "").strip()
    query = StudentProfile.query.join(User)
    if q:
        query = query.filter(User.name.ilike(f"%{q}%"))
    students = query.all()
    result = []
    for s in students:
        d = s.to_dict()
        d["user"] = s.user.to_dict()
        result.append(d)
    return jsonify(result)


@admin_bp.route("/students/<int:student_id>/toggle-active", methods=["POST"])
@role_required("admin")
def toggle_student_active(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student.user.is_active = not student.user.is_active
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Student status toggled", "student": student.to_dict()})


@admin_bp.route("/drives", methods=["GET"])
@role_required("admin")
def list_all_drives():
    status = request.args.get("status")
    query = Drive.query
    if status:
        query = query.filter_by(status=status)
    drives = query.order_by(Drive.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives])


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["POST"])
@role_required("admin")
def approve_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    drive.status = "approved"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Drive approved", "drive": drive.to_dict()})


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["POST"])
@role_required("admin")
def reject_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    drive.status = "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Drive rejected", "drive": drive.to_dict()})


@admin_bp.route("/applications", methods=["GET"])
@role_required("admin")
def list_all_applications():
    apps = Application.query.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps])

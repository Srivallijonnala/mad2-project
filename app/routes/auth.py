from flask import Blueprint, request, jsonify, session

from app.extensions import db
from app.models import User, StudentProfile, CompanyProfile
from app.utils.decorators import get_current_user, login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email, role="student")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  

    profile = StudentProfile(
        user_id=user.id,
        branch=data.get("branch"),
        year=data.get("year"),
        cgpa=data.get("cgpa"),
        phone=data.get("phone"),
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Student registered successfully", "user": user.to_dict()}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    company_name = (data.get("company_name") or "").strip()

    if not name or not email or not password or not company_name:
        return jsonify({"error": "name, email, password and company_name are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email, role="company")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    profile = CompanyProfile(
        user_id=user.id,
        company_name=company_name,
        hr_contact=data.get("hr_contact"),
        website=data.get("website"),
        approval_status="pending",
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({
        "message": "Company registered successfully. Awaiting admin approval.",
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    if not user.is_active or user.is_blacklisted:
        return jsonify({"error": "Account is deactivated or blacklisted"}), 403
    if user.role == "company" and user.company_profile.approval_status != "approved":
        return jsonify({
            "error": f"Company account is '{user.company_profile.approval_status}'. "
                     f"Wait for admin approval."
        }), 403

    session.clear()
    session["user_id"] = user.id
    session["role"] = user.role
    session.permanent = True

    return jsonify({"message": "Login successful", "user": user.to_dict()})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    user = get_current_user()
    data = user.to_dict()
    if user.role == "student" and user.student_profile:
        data["profile"] = user.student_profile.to_dict()
    elif user.role == "company" and user.company_profile:
        data["profile"] = user.company_profile.to_dict()
    return jsonify(data)

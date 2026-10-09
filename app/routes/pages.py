from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/", defaults={"path": ""})
@pages_bp.route("/<path:path>")
def index(path):
    """Always serve the same SPA shell. Vue's client-side router decides what to
    render based on window.location.pathname, and also handles auth-based redirects.
    This also makes hard-refreshing on a deep link (e.g. /student/dashboard) work."""
    return render_template("index.html")


from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created.")

    admin_email = app.config["ADMIN_LOGIN_EMAIL"]
    existing_admin = User.query.filter_by(role="admin").first()

    if existing_admin:
        print(f"Admin already exists: {existing_admin.email}")
    else:
        admin = User(
            name=app.config["ADMIN_NAME"],
            email=admin_email,
            role="admin",
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(f"Seeded admin user -> email: {admin_email} | password: {app.config['ADMIN_PASSWORD']}")
        print("Change ADMIN_PASSWORD via environment variable for anything beyond local demo use.")

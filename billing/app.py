from datetime import datetime, date
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dash_bp
    from routes.clients import clients_bp
    from routes.invoices import invoices_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(invoices_bp)

    @app.context_processor
    def inject_globals():
        return {"now": datetime.utcnow(), "today": date.today()}

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Create default admin on first run."""
    if not User.query.filter_by(role="admin").first():
        admin = User(
            username="admin",
            email="admin@maverickinfra.com.np",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("=" * 50)
        print("  Default admin created")
        print("  Username : admin")
        print("  Password : admin123")
        print("  → Change this after first login!")
        print("=" * 50)


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

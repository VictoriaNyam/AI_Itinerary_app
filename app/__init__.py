# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# Initialize core extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_pyfile('../instance/config.py')

    # Set up upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'static',
        'uploads'
    )
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions with app
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # Import models and set up user loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    # Auto-create all tables immediately on app startup
    with app.app_context():
        db.create_all()

    # Optional: Admin user creation block (uncomment if needed)
    """
    def create_admin_user():
        with app.app_context():
            admin_email = "admin@example.com"
            admin_user = User.query.filter_by(email=admin_email).first()
            if not admin_user:
                hashed_pw = bcrypt.generate_password_hash("admin123").decode("utf-8")
                admin = User(username="admin", email=admin_email, password=hashed_pw, is_admin=True)
                db.session.add(admin)
                db.session.commit()
                print("Admin user created.")
            else:
                print("Admin user already exists.")

    create_admin_user()
    """

    return app

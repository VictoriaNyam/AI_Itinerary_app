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

    # Import User model for user loader and admin seeding
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    # Auto-create all tables and seed admin user
    with app.app_context():
        db.create_all()

        # Seed admin user if not already present
        def create_admin_user():
    # Ensure the table is created before trying to insert
    db.create_all()

    # Check if the admin user already exists
    admin = User.query.filter_by(username="admin").first()

    if admin is None:
        admin_email = "admin@example.com"
        admin_password = "admin123"
        
        # Create the user but don't pass the password directly
        admin = User(username="admin", email=admin_email, is_admin=True)
        
        # Set the password using the method
        admin.set_password(admin_password)
        
        # Add and commit the new admin user to the database
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists.")


    return app

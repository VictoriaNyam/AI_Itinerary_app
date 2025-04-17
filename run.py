from flask import Flask
from app.models import db  

def create_app():
    app = Flask(__name__)

    # app config here (e.g., secret key, db URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'your-database-url'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Create tables here
    @app.before_first_request
    def create_tables():
        db.create_all()

    # Register blueprints here (if any)
    return app

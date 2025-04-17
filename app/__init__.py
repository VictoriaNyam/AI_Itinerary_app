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

    app.config.from_pyfile('../instance/config.py')

    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main
    app.register_blueprint(main)

    # ✅ Auto-create admin user if not already in DB
   # def create_admin_user():
      #  with app.app_context():
           # admin_email = "admin@example.com"
           # admin_user = User.query.filter_by(email=admin_email).first()
          #  if not admin_user:
               # hashed_pw = bcrypt.generate_password_hash("admin123").decode("utf-8")
               # admin = User(username="admin", email=admin_email, password=hashed_pw, is_admin=True)
               # db.session.add(admin)
              #  db.session.commit()
              #  print("✅ Admin user created.")
          #  else:
                #print("ℹ️ Admin user already exists.")

    #create_admin_user()  # 🔁 Run the admin creation function

   # return app

# Create the app instance
app = create_app()

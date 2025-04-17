# instance/config.py
import os

SECRET_KEY = 'asecretkey12345678'

# Use environment variable if it exists, otherwise default to local SQLite
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

from datetime import datetime  
from app import db, bcrypt  # Database and password hashing  
from flask_login import UserMixin  # Session management for users

# User model

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # User can create multiple itineraries and uploads
    itineraries = db.relationship(
        'Itinerary', back_populates='user', cascade='all, delete-orphan'
    )
    uploads = db.relationship(
        'Upload', back_populates='user', cascade='all, delete-orphan', passive_deletes=True
    )
    likes = db.relationship(
        'Like', back_populates='user', cascade='all, delete-orphan', passive_deletes=True
    )
    comments = db.relationship(
        'Comment', back_populates='user', cascade='all, delete-orphan', passive_deletes=True
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Itinerary model

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    pois = db.relationship(
        'POI', back_populates='itinerary', cascade='all, delete-orphan'
    )
    user = db.relationship('User', back_populates='itineraries')

    def __repr__(self):
        return f'<Itinerary {self.name}>'



# POI model

class POI(db.Model):
    __tablename__ = 'poi'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    original_latitude = db.Column(db.Float)
    original_longitude = db.Column(db.Float)
    day = db.Column(db.Integer, nullable=False)
    itinerary_id = db.Column(
        db.Integer, db.ForeignKey('itinerary.id', ondelete='CASCADE'), nullable=False
    )

    itinerary = db.relationship('Itinerary', back_populates='pois')

    def __repr__(self):
        return f"<POI {self.name}>"



# Upload model

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    upload_type = db.Column(db.String(10), nullable=False)  
    filename = db.Column(db.String(120), nullable=True)
    vlog_url = db.Column(db.String(255), nullable=True)
    vlog_title = db.Column(db.String(120), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='uploads')
    likes = db.relationship(
        'Like', back_populates='upload', cascade='all, delete-orphan', passive_deletes=True
    )
    comments = db.relationship(
        'Comment', back_populates='upload', cascade='all, delete-orphan', passive_deletes=True
    )

    def __repr__(self):
        return f'<Upload {self.id}>'



# Like model

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    upload_id = db.Column(
        db.Integer, db.ForeignKey('upload.id', ondelete='CASCADE'), nullable=False
    )

    user = db.relationship('User', back_populates='likes')
    upload = db.relationship('Upload', back_populates='likes')

    def __repr__(self):
        return f'<Like {self.id}>'



# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    upload_id = db.Column(
        db.Integer, db.ForeignKey('upload.id', ondelete='CASCADE'), nullable=False
    )
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='comments')
    upload = db.relationship('Upload', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'

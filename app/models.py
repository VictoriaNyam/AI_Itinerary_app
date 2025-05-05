from datetime import datetime  
from app import db, bcrypt  # Database and password hashing  
from flask_login import UserMixin  # Session management for users


# User model

class User(UserMixin, db.Model):
    # Unique identifier for the user
    id = db.Column(db.Integer, primary_key=True)  
    # Username (must be unique)
    username = db.Column(db.String(100), unique=True, nullable=False)  
    # Email address (must be unique)
    email = db.Column(db.String(100), unique=True, nullable=False)  
    # Hashed password
    password_hash = db.Column(db.String(128), nullable=False)  
    # Timestamp when the user joined
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  
    # Flag for admin users
    is_admin = db.Column(db.Boolean, default=False)  

    # One-to-many relationship: a user can have multiple itineraries
    itineraries = db.relationship(
        'Itinerary', back_populates='user', cascade='all, delete-orphan'
    )
    # One-to-many relationship: a user can upload multiple blogs/vlogs
    uploads = db.relationship(
        'Upload', back_populates='user', cascade='all, delete-orphan', passive_deletes=True
    )

    def __repr__(self):
        return f'<User {self.username}>'

    # Hash and set the user's password
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Verify a provided password against the hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# Itinerary model

class Itinerary(db.Model):
    # Unique identifier for the itinerary
    id = db.Column(db.Integer, primary_key=True)  
    # Foreign key linking to the user who created the itinerary
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    # Name given to the itinerary
    name = db.Column(db.String(100), nullable=False)  
    # Creation timestamp
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  

    # One-to-many: an itinerary contains multiple POIs
    pois = db.relationship(
        'POI', back_populates='itinerary', cascade='all, delete-orphan'
    )
    # Many-to-one: link back to the creating user
    user = db.relationship('User', back_populates='itineraries')

    def __repr__(self):
        return f'<Itinerary {self.name}>'


# POI (Point of Interest) model

class POI(db.Model):
    __tablename__ = 'poi'  # Explicit table name to avoid conflicts

    # Unique identifier for the POI
    id = db.Column(db.Integer, primary_key=True)  
    # Name of the point of interest
    name = db.Column(db.String(255), nullable=False)  
    # Optional address
    address = db.Column(db.String(255))  
    # Geolocation fields
    latitude = db.Column(db.Float)  
    longitude = db.Column(db.Float)  
    original_latitude = db.Column(db.Float)  
    original_longitude = db.Column(db.Float)  
    # Day number in the itinerary
    day = db.Column(db.Integer, nullable=False)  
    # Foreign key linking to the itinerary
    itinerary_id = db.Column(
        db.Integer, db.ForeignKey('itinerary.id', ondelete='CASCADE'), nullable=False
    )

    # Link back to the itinerary
    itinerary = db.relationship('Itinerary', back_populates='pois')

    def __repr__(self):
        return f"<POI {self.name}>"


# Upload model for Blogs/Vlogs

class Upload(db.Model):
    # Unique identifier for each upload
    id = db.Column(db.Integer, primary_key=True)  
    # Foreign key linking to the uploading user
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    # Type of content: 'blog' or 'vlog'
    upload_type = db.Column(db.String(10), nullable=False)  
    # For blogs: filename in uploads folder
    filename = db.Column(db.String(120), nullable=True)  
    # For vlogs: external URL or file path
    vlog_url = db.Column(db.String(255), nullable=True)  
    # Optional title for the vlog
    vlog_title = db.Column(db.String(120), nullable=True)  
    # Timestamp of when the upload was created
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())  

    # Many-to-one: link back to the user
    user = db.relationship('User', back_populates='uploads')
    # One-to-many: an upload can have many likes
    likes = db.relationship(
        'Like', back_populates='upload', cascade='all, delete-orphan', passive_deletes=True
    )
    # One-to-many: an upload can have many comments
    comments = db.relationship(
        'Comment', back_populates='upload', cascade='all, delete-orphan', passive_deletes=True
    )

# Like model for user likes
class Like(db.Model):
    # Unique identifier for the like
    id = db.Column(db.Integer, primary_key=True)  
    # Foreign key linking to the liking user
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    # Foreign key linking to the liked upload
    upload_id = db.Column(
        db.Integer, db.ForeignKey('upload.id', ondelete='CASCADE'), nullable=False
    )

    # Many-to-one: link back to the user
    user = db.relationship('User', backref='likes')
    # Many-to-one: link back to the upload
    upload = db.relationship('Upload', back_populates='likes')

    def __repr__(self):
        return f'<Like {self.id}>'

# Comment model for user comments

class Comment(db.Model):
    # Unique identifier for the comment
    id = db.Column(db.Integer, primary_key=True)  
    # Foreign key linking to the commenting user
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    # Foreign key linking to the commented upload
    upload_id = db.Column(
        db.Integer, db.ForeignKey('upload.id', ondelete='CASCADE'), nullable=False
    )
    # Text content of the comment
    content = db.Column(db.Text, nullable=False)  
    # Timestamp of when the comment was made
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  

    # Many-to-one: link back to the user
    user = db.relationship('User', backref='comments')
    # Many-to-one: link back to the upload
    upload = db.relationship('Upload', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'

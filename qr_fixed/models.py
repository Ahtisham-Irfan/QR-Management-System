from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    qrs = db.relationship('QRCode', backref='owner', lazy=True)
    logs = db.relationship('ActivityLog', backref='user', lazy=True)

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    qr_type = db.Column(db.String(50), nullable=False)  # URL, Text, WiFi, etc.
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    downloads = db.Column(db.Integer, default=0)
    
    # Customization settings
    fill_color = db.Column(db.String(20), default="#000000")
    back_color = db.Column(db.String(20), default="#FFFFFF")
    has_logo = db.Column(db.Boolean, default=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    qrs = db.relationship('QRCode', backref='category', lazy=True)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    details = db.Column(db.Text)

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    wines = db.relationship('Wine', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'

class Wine(db.Model):
    __tablename__ = 'wines'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Wine details
    vineyard = db.Column(db.String(200))
    varietal = db.Column(db.String(100))
    vintage = db.Column(db.Integer)
    date_had = db.Column(db.Date)
    origin = db.Column(db.String(200))
    rating = db.Column(db.Float)
    purchase_location = db.Column(db.String(200))
    wine_club_month = db.Column(db.String(50))
    price = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    # Additional features
    photo_filename = db.Column(db.String(255))
    is_favorite = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vineyard': self.vineyard,
            'varietal': self.varietal,
            'vintage': self.vintage,
            'date_had': self.date_had.isoformat() if self.date_had else None,
            'origin': self.origin,
            'rating': self.rating,
            'purchase_location': self.purchase_location,
            'wine_club_month': self.wine_club_month,
            'price': self.price,
            'notes': self.notes,
            'photo_filename': self.photo_filename,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

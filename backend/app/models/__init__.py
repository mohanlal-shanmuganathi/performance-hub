from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('admin', 'manager', 'employee', name='user_roles'), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hire_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', remote_side=[id], backref='direct_reports')
    goals = db.relationship('Goal', backref='employee', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    target_date = db.Column(db.Date)
    status = db.Column(db.Enum('draft', 'active', 'completed', 'cancelled', name='goal_status'), default='draft')
    progress = db.Column(db.Integer, default=0)
    manager_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_type = db.Column(db.Enum('self', 'peer', 'manager', name='review_types'), nullable=False)
    review_period = db.Column(db.String(20))
    overall_rating = db.Column(db.Integer)
    technical_skills = db.Column(db.Integer)
    communication = db.Column(db.Integer)
    leadership = db.Column(db.Integer)
    teamwork = db.Column(db.Integer)
    comments = db.Column(db.Text)
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    status = db.Column(db.Enum('draft', 'submitted', 'completed', name='review_status'), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency_level = db.Column(db.Integer)  # 1-5 scale
    category = db.Column(db.String(50))
    last_assessed = db.Column(db.Date)
    target_level = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('User', backref='skills')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')
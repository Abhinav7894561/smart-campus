from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
    class_time = db.Column(db.String(10), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)

class ClassStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    substitute_name = db.Column(db.String(100), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    schedule = db.relationship('Schedule', backref='statuses')
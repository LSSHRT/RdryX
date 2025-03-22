from app import db
from datetime import datetime

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<Config {self.name}>'


class SurveyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    age_group = db.Column(db.String(50), nullable=False)
    restaurant_number = db.Column(db.String(10), nullable=False)
    receipt_date = db.Column(db.String(20), nullable=False)
    receipt_time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='success')
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<SurveyLog {self.submission_date}>' 
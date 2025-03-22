from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models.config import SurveyLog
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page"""
    # Get statistics
    total_surveys = SurveyLog.query.count()
    successful_surveys = SurveyLog.query.filter_by(status='success').count()
    failed_surveys = SurveyLog.query.filter_by(status='error').count()
    
    # Get recent logs (last 10)
    recent_logs = SurveyLog.query.order_by(SurveyLog.submission_date.desc()).limit(10).all()
    
    return render_template('index.html', 
                           total_surveys=total_surveys,
                           successful_surveys=successful_surveys,
                           failed_surveys=failed_surveys,
                           recent_logs=recent_logs)

@main_bp.route('/logs')
def logs():
    """View all survey logs"""
    page = request.args.get('page', 1, type=int)
    logs_per_page = 20
    
    logs = SurveyLog.query.order_by(SurveyLog.submission_date.desc()).paginate(
        page=page, per_page=logs_per_page, error_out=False)
    
    return render_template('logs.html', logs=logs) 
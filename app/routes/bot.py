from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from app import db
from app.models.config import SurveyLog
from app.controllers.bot_controller import McDoSurveyBot
from datetime import datetime
import threading

bot_bp = Blueprint('bot', __name__)

# Global variable to track if the bot is running
bot_running = False
bot_thread = None

@bot_bp.route('/')
def bot_control():
    """Bot control panel"""
    global bot_running
    return render_template('bot_control.html', bot_running=bot_running)

@bot_bp.route('/run', methods=['POST'])
def run_bot():
    """Run the survey bot once"""
    global bot_running, bot_thread
    
    if bot_running:
        flash('Bot is already running!', 'warning')
        return redirect(url_for('bot.bot_control'))
    
    # Get parameters from form
    age_group = request.form.get('age_group')
    date = request.form.get('date')
    time = request.form.get('time')
    restaurant_number = request.form.get('restaurant_number')
    headless = 'headless' in request.form
    
    # Store the current application for use in the thread
    app = current_app._get_current_object()
    
    # Run the bot in a separate thread
    def run_survey_thread():
        global bot_running
        bot_running = True
        try:
            # Create a fresh application context for this thread
            with app.app_context():
                try:
                    bot = McDoSurveyBot(headless=headless)
                    result = bot.run_survey(
                        age_group=age_group, 
                        date=date, 
                        hour_time=time,
                        restaurant_number=restaurant_number
                    )
                    
                    # Log the result
                    log = SurveyLog(
                        age_group=result['data']['age_group'] or 'unknown',
                        restaurant_number=result['data']['restaurant_number'] or 'unknown',
                        receipt_date=result['data']['date'] or 'unknown',
                        receipt_time=result['data']['time'] or 'unknown',
                        status=result['status'],
                        error_message=result.get('message') if result['status'] == 'error' else None
                    )
                    
                    db.session.add(log)
                    db.session.commit()
                    
                except Exception as e:
                    # Log any unexpected errors
                    log = SurveyLog(
                        age_group=age_group or 'unknown',
                        restaurant_number=restaurant_number or 'unknown',
                        receipt_date=date or 'unknown',
                        receipt_time=time or 'unknown',
                        status='error',
                        error_message=str(e)
                    )
                    
                    db.session.add(log)
                    db.session.commit()
        except Exception as e:
            print(f"Unexpected error in thread: {str(e)}")
        finally:
            bot_running = False
    
    bot_thread = threading.Thread(target=run_survey_thread)
    bot_thread.daemon = True
    bot_thread.start()
    
    flash('Bot started!', 'success')
    return redirect(url_for('bot.bot_control'))

@bot_bp.route('/bulk', methods=['POST'])
def run_bulk():
    """Run multiple surveys in bulk"""
    global bot_running, bot_thread
    
    if bot_running:
        flash('Bot is already running!', 'warning')
        return redirect(url_for('bot.bot_control'))
    
    # Get parameters from form
    count = int(request.form.get('count', 1))
    if count < 1:
        count = 1
    elif count > 50:  # Limit to 50 for safety
        count = 50
        
    # Get interval in minutes between surveys
    interval = int(request.form.get('interval', 5))
    if interval < 1:
        interval = 1
    elif interval > 60:  # Limit to 60 minutes
        interval = 60
        
    headless = 'headless' in request.form
    
    # Store the current application for use in the thread
    app = current_app._get_current_object()
    
    # Run the bot in a separate thread
    def run_bulk_thread():
        global bot_running
        bot_running = True
        
        try:
            # Create a fresh application context for this thread
            with app.app_context():
                try:
                    # Utiliser la nouvelle méthode run_bulk_surveys
                    bot = McDoSurveyBot(headless=headless)
                    bulk_result = bot.run_bulk_surveys(
                        count=count,
                        interval_minutes=interval
                    )
                    
                    # Traiter les résultats et les enregistrer dans la base de données
                    if 'results' in bulk_result:
                        for result in bulk_result['results']:
                            # Log chaque résultat individuel
                            if 'data' in result:
                                log = SurveyLog(
                                    age_group=result['data'].get('age_group', 'unknown'),
                                    restaurant_number=result['data'].get('restaurant_number', 'unknown'),
                                    receipt_date=result['data'].get('date', 'unknown'),
                                    receipt_time=result['data'].get('time', 'unknown'),
                                    status=result['status'],
                                    error_message=result.get('message') if result['status'] == 'error' else None
                                )
                                
                                db.session.add(log)
                        
                        db.session.commit()
                        
                except Exception as e:
                    # Log any unexpected errors
                    log = SurveyLog(
                        age_group='unknown',
                        restaurant_number='unknown',
                        receipt_date='unknown',
                        receipt_time='unknown',
                        status='error',
                        error_message=f"Bulk operation error: {str(e)}"
                    )
                    
                    db.session.add(log)
                    db.session.commit()
                    
        except Exception as e:
            print(f"Unexpected error in bulk thread: {str(e)}")
        finally:
            bot_running = False
    
    bot_thread = threading.Thread(target=run_bulk_thread)
    bot_thread.daemon = True
    bot_thread.start()
    
    flash(f'Started bulk operation with {count} surveys and {interval} minute intervals!', 'success')
    return redirect(url_for('bot.bot_control'))

@bot_bp.route('/status')
def bot_status():
    """Check the bot status"""
    global bot_running
    return jsonify({
        'running': bot_running
    }) 
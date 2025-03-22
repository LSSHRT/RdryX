from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-key-for-dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from app.routes.main import main_bp
    from app.routes.bot import bot_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(bot_bp, url_prefix='/bot')
    
    with app.app_context():
        db.create_all()
    
    return app 
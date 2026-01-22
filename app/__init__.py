import os
from flask import Flask
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from app.models import db, User
from app.backup import backup_database

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.environ.get('DATABASE_PATH', 'data/wines.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import main
    from app.auth import auth
    from app.admin import admin
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    
    # Setup automated backups (daily at 2 AM)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: backup_database(app),
        trigger="cron",
        hour=2,
        minute=0
    )
    scheduler.start()
    
    return app

# app.py
import os
from flask import Flask, send_from_directory
from flask_wtf.csrf import CSRFProtect
from flasgger import Swagger
from flask_jwt_extended import JWTManager, jwt_required
from utils import parse_datetime
from celery_worker import celery

# Use new paths for imports
from core.extensions import db, cache, csrf, mail
from core.extensions import db, cache, csrf, mail
from core.models import User, Role, SecretQuestion
from config import DevelopmentConfig as AppConfig

from core.models import User, Role, SecretQuestion
from config import DevelopmentConfig as AppConfig
from werkzeug.security import generate_password_hash
from flask_debugtoolbar import DebugToolbarExtension

from flask_apscheduler import APScheduler
from celery.schedules import crontab


try:
    from api.auth import definitions as api_auth_definitions
    api_definitions = {**api_auth_definitions} 
except ImportError:
    print("Warning: Could not import API definitions. Swagger might be incomplete.")
    api_definitions = {}

# App Setup 
app = Flask(__name__, 
            instance_relative_config=True,
            static_folder='../frontend/dist', 
            static_url_path='/'
            )
app.config.from_object(AppConfig)

app.config['SWAGGER'] = {
    'title': 'Quiz App API',
    'uiversion': 3,
    "specs_route": "/apidocs/",
    'definitions': api_definitions
}

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "My API",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: **Bearer &lt;your JWT token&gt;**"
        }
    }
})

# Flask-DebugToolbar Configuration
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your_super_secret_key_for_debug_toolbar'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

# Flask-Caching Configuration for Redis 
app.config['CACHE_TYPE'] = 'RedisCache' 
app.config['CACHE_REDIS_HOST'] = 'localhost' 
app.config['CACHE_REDIS_PORT'] = 6379      
app.config['CACHE_REDIS_DB'] = 0         
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0' 

celery.conf.broker_url = app.config['CELERY_BROKER_URL']
celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
celery.conf.update(app.config)

# Define the ContextTask here, where 'app' is available
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# Define the Celery Beat schedule here
celery.conf.beat_schedule = {
    'send-monthly-reports': {
        'task': 'jobs.send_monthly_reports', 
        'schedule': crontab(day_of_month='1', hour=8, minute=0), 
    },
}
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# --- Initialize Extensions ---
db.init_app(app)
jwt = JWTManager(app)
cache.init_app(app)
csrf.init_app(app)
mail.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from jobs import send_daily_reminders

if not scheduler.get_job('daily-reminders'):
    scheduler.add_job(
        id='daily-reminders', 
        func=send_daily_reminders, 
        #trigger='interval',
        #minutes=1
        trigger='cron', 
        hour=20, 
        
    )
    #print("TESTING: Scheduled 'daily-reminders' job to run every 1 minute.")
    print("Scheduled 'daily-reminders' job to run every day at 20:00.")


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"] 
    return User.query.filter_by(fs_uniquifier=identity).first()

def create_initial_data():
    """Creates roles, secret questions, and the default admin user."""
    # --- Create Roles ---
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
        print("Created 'admin' role.")

    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular User')
        db.session.add(user_role)
        print("Created 'user' role.")

    # --- Create Secret Questions ---
    if SecretQuestion.query.count() == 0:
        print("Creating default secret questions...")
        questions = [
            "What was the name of your first pet?",
            "What is your mother's maiden name?",
            "What was the name of your elementary school?",
            "In what city were you born?",
            "What is your favorite book?"
        ]
        for q_text in questions:
            db.session.add(SecretQuestion(text=q_text))
    
    # --- Create Admin User ---
    admin_user = User.query.join(User.roles).filter(Role.name == 'admin').first()
    if not admin_user:
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Thisisadmin@123')
        
        # Get the first secret question to assign to the admin
        default_secret_question = SecretQuestion.query.first()
        if not default_secret_question:
            print("ERROR: Could not find a default secret question for the admin user.")
            db.session.rollback()
            return

        admin_secret_answer = "adminpet"

        if not User.query.filter_by(username=admin_username).first():
            admin_user = User(
                username=admin_username,
                email=admin_email,
                active=True,
                secret_question_id=default_secret_question.id
            )
            admin_user.set_password(admin_password)
            admin_user.set_secret_answer(admin_secret_answer) 
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            print(f"Created admin user: {admin_username}")
        else:
            print("Admin username already exists, cannot create default admin.")

    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing initial data: {e}")
        db.session.rollback()


# Register the function as a Jinja filter
app.jinja_env.filters['timedeltaformat'] = parse_datetime

# --- Register Blueprints ---
from main.routes import main_bp 
from api.auth import auth_api_bp 
from api.subjects import subjects_api_bp 
from api.chapters import chapters_api_bp
from api.quizzes import quizzes_api_bp
from api.questions import questions_api_bp
from api.users import users_api_bp
from api.attempts import attempts_api_bp
from api.search_api import search_api_bp
from api.summary_api import summary_api_bp
from api.user_api import user_api_bp 
from api.admin_api import admin_api_bp
from api.export_api import export_api_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_api_bp, url_prefix='/api/auth')
app.register_blueprint(subjects_api_bp, url_prefix='/api/subjects')
app.register_blueprint(chapters_api_bp, url_prefix='/api/chapters')
app.register_blueprint(quizzes_api_bp, url_prefix='/api/quizzes')
app.register_blueprint(questions_api_bp, url_prefix='/api') 
app.register_blueprint(users_api_bp, url_prefix='/api/users')
app.register_blueprint(attempts_api_bp, url_prefix='/api/attempts')
app.register_blueprint(search_api_bp, url_prefix='/api/search')
app.register_blueprint(summary_api_bp, url_prefix='/api/summary')
app.register_blueprint(user_api_bp, url_prefix='/api/user')
app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
app.register_blueprint(export_api_bp, url_prefix='/api')

from flask import send_from_directory

@app.route('/exports/<path:filename>')
@jwt_required() # Secure the download link
def download_export(filename):
    """Serves files from the secure export directory."""
    export_dir = os.path.join(app.instance_path, 'exports')
    return send_from_directory(export_dir, filename, as_attachment=True)

csrf.exempt(auth_api_bp)
csrf.exempt(subjects_api_bp)
csrf.exempt(chapters_api_bp)
csrf.exempt(quizzes_api_bp)
csrf.exempt(questions_api_bp)
csrf.exempt(users_api_bp)
csrf.exempt(attempts_api_bp)
csrf.exempt(search_api_bp)
csrf.exempt(summary_api_bp)
csrf.exempt(user_api_bp)
csrf.exempt(admin_api_bp)
csrf.exempt(export_api_bp)


# --- Run the App ---
if __name__ == '__main__':
    with app.app_context():
        print("Initializing database...")
        db.create_all()
        print("Checking initial data (roles, questions, admin)...")
        create_initial_data()
        print("Initialization complete.")

    app.run(debug=True, port=5000)

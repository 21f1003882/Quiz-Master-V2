# config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'change-this-jwt-secret-key-now'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-please-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db') # Store DB in instance folder
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'a-very-secret-salt-change-this'
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False 

    CELERY_BROKER_URL = 'redis://localhost:6379/1' 
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

    SCHEDULER_API_ENABLED = True

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    SWAGGER = {
    'title': 'Quiz App API',
    'uiversion': 3,
    "specs_route": "/apidocs/"
}

DevelopmentConfig = Config 
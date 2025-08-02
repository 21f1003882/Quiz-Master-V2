# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

db = SQLAlchemy()
cache = Cache()
csrf = CSRFProtect() 
mail = Mail()
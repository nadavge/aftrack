from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
# TODO change after production
from aftrack.config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from aftrack.utils import generate_csrf_token

app.jinja_env.globals['csrf_token'] = generate_csrf_token

from aftrack import views


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
# TODO change after production
from aftrack.config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db = SQLAlchemy(app)

login_manager = LoginManager()
# TODO setup login view
# login_manager.login_view = "NAME"
login_manager.init_app(app)

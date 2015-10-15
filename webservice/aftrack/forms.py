from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required

from aftrack.models import User

class LoginForm(Form):
	username = TextField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])

from flask.ext.wtf import Form
from sqlalchemy import func
from wtforms import TextField, PasswordField, IntegerField
from wtforms.validators import (Required,
		Length, EqualTo, Regexp, ValidationError)
from aftrack.models import User

def length_kwargs(min, max):
	return {'min': min,
			'max': max,
			'message': 'Length in range %d-%d.'%(min, max)}

class LoginForm(Form):
	username = TextField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])

class SignupForm(Form):
	username = TextField('Username', validators=[
			Required(),
			Regexp('^[A-z\d]+$', message='Only alpha-numeric allowed.'),
			Length(**length_kwargs(User.MIN_USERNAME, User.MAX_USERNAME))])
	password = PasswordField('Password', validators=[
			Required(),
			Length(**length_kwargs(User.MIN_PASSWORD, User.MAX_PASSWORD))])
	repassword = PasswordField('Repeat password', validators=[
			Required(),
			EqualTo('password', 'Passwords don\'t match')])
	first_name = TextField('First name', validators=[
			Required(),
			Regexp("^[A-z][A-z ',-]+$", message='Invalid characters.'),
			Length(**length_kwargs(User.MIN_FIRST_NAME, User.MAX_FIRST_NAME))])
	last_name = TextField('Last name', validators=[
			Required(),
			Regexp("^[A-z][A-z ',-]*$", message='Invalid characters.'),
			Length(**length_kwargs(User.MIN_LAST_NAME, User.MAX_LAST_NAME))])
	yearbook = IntegerField('Yearbook', validators=[Required()])

	def validate_username(self, field):
		user = User.query.filter(
			func.lower(User.username) == func.lower(field.data)
		).first()
		if user:
			raise ValidationError(
					'Username already taken.'
			)
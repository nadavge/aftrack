from flask.ext.wtf import Form
from sqlalchemy import func
from wtforms import TextField, PasswordField, IntegerField
from wtforms.validators import (Required,
		Length, EqualTo, Regexp, ValidationError)
from aftrack.models import User
from datetime import datetime, timedelta

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


class ProfileEditForm(Form):
	first_name = TextField('First name', validators=[
			Required(),
			Regexp("^[A-z][A-z ',-]+$", message='Invalid characters.'),
			Length(**length_kwargs(User.MIN_FIRST_NAME, User.MAX_FIRST_NAME))])
	last_name = TextField('Last name', validators=[
			Required(),
			Regexp("^[A-z][A-z ',-]*$", message='Invalid characters.'),
			Length(**length_kwargs(User.MIN_LAST_NAME, User.MAX_LAST_NAME))])


class ChangePasswordForm(Form):
	old_password = PasswordField('Old password', validators=[Required()])
	new_password = PasswordField('New password', validators=[
			Required(),
			Length(**length_kwargs(User.MIN_PASSWORD, User.MAX_PASSWORD))])
	repassword = PasswordField('Repeat password', validators=[
			Required(),
			EqualTo('new_password', 'Passwords don\'t match')])

	def __init__(self, user):
		super().__init__()
		self.user = user

	def validate_old_password(self, field):
		password = field.data
		if not self.user.check_password(password):
			raise ValidationError(
				'Wrong password'
			)


def validate_time(time_str):
	try:
		datetime.strptime(time_str, '%H:%M')
	except ValueError:
		raise ValidationError(
			'Invalid time'
		)

class AfterForm(Form):
	date = TextField('Date')
	start = TextField('Start')
	end = TextField('End')

	def validate_date(self, field):
		try:
			datetime.strptime(field.data, '%d/%m/%Y')
		except ValueError:
			raise ValidationError(
				'Invalid date'
			)

	def validate_start(self, field):
		validate_time(field.data)

	def validate_end(self, field):
		validate_time(field.data)

	def parse(self):
		"""Parse the form, and return a tuple of the
		*local* start and enddatetimes"""
		local_date = datetime.strptime(self.date.data, '%d/%m/%Y').date()
		local_start_time = datetime.strptime(self.start.data, '%H:%M').time()
		local_start = datetime.combine(local_date, local_start_time)

		local_end_time = datetime.strptime(self.end.data, '%H:%M').time()
		local_end = datetime.combine(local_date, local_end_time)
		# In case the end was after midnight
		if local_end < local_start:
			local_end += timedelta(days=1)

		return local_start, local_end


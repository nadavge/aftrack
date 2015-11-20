from aftrack import app, db, login_manager
from flask.ext.login import make_secure_token, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimedSerializer
from datetime import time, datetime, timedelta
from sqlalchemy import func
from aftrack.utils.sqlalchemy_types import TimezoneType
import pytz

PASSWORD_HASH_LEN = 66 # Based on generate_password_hash output
NEW_DAY_TIME = time(6,0) # 06:00 (AM)
UTC_TZ = pytz.timezone('utc')


class User(db.Model, UserMixin):
	MIN_USERNAME = 5
	MIN_PASSWORD = 8
	MIN_FIRST_NAME = 2
	MIN_LAST_NAME = 2
	MAX_USERNAME = 16
	MAX_PASSWORD = 20
	MAX_FIRST_NAME = 12
	MAX_LAST_NAME = 20

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(16), unique=True)
	password = db.Column(db.String(66))
	first_name = db.Column(db.String(12))
	last_name = db.Column(db.String(20))
	yearbook = db.Column(db.Integer)
	admin = db.Column(db.Boolean, default=False)
	timezone = db.Column(TimezoneType, default=pytz.timezone('Asia/Jerusalem'))
	afters = db.relationship('After', backref='user')

	@staticmethod
	def authenticate(username, password):
		"""Authenticate a user through a login form of some sort"""
		user = User.get_by_username(username)
		if user and user.check_password(password):
			return user
		return None

	@staticmethod
	def get_by_username(username):
		user = User.query.filter(
			func.lower(User.username) == func.lower(username)
		).first()
		return user

	def __init__(self, username, password, first_name, last_name,
			yearbook, admin=False):
		"""Construct a now user, based on given parameters.
		Password is generated, and there's no need to use the set_password"""
		self.username = username
		self.set_password(password)
		self.first_name = first_name
		self.last_name = last_name
		self.yearbook = yearbook
		self.admin = admin

	@property
	def hmac(self):
		"""An hmac usefol for the token authentication through a cookie"""
		return make_secure_token(self.username, self.password)

	@property
	def full_name(self):
		"""Concatenate the last name to the first name"""
		return '%s %s'%(self.first_name, self.last_name)

	def local_datetime(self, utc_datetime=None):
		"""Converts datetime to local datetime, if no datetime given returns
		current datetime"""
		if utc_datetime is None:
			utc_datetime = datetime.utcnow()

		utc_datetime = UTC_TZ.localize(utc_datetime)
		return self.timezone.normalize(utc_datetime.astimezone(self.timezone))

	def utc_datetime(self, local_datetime=None):
		"""Converts a local datetime to utc datetime, if no datetime given
		returns	current datetime"""
		if local_datetime is None:
			return datetime.utcnow()

		local_datetime = self.timezone.localize(local_datetime)
		return UTC_TZ.normalize(local_datetime.astimezone(UTC_TZ))

	def get_auth_token(self):
		"""Generate auth token for cookie usage """
		serializer = TimedSerializer(app.secret_key)
		data = (self.id, self.hmac)
		return serializer.dumps(data)

	def check_password(self, password):
		"""Checks if plaintext password matches hashed password in db """
		return check_password_hash(self.password, password)

	def set_password(self, password):
		"""Hashes password and saves it in the user object

		note: doesn't handle commiting to db """
		self.password = generate_password_hash(password)

	def get_active_after(self):
		"""Return the active after object, None if no active after"""
		for after in self.afters:
			if after.end is None: return after
		return None


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)


@login_manager.token_loader
def load_token(token):
	""" Loads the user from a token, made of the user id and hmac
	signed by itsdangerous """
	serializer = TimedSerializer(app.secret_key)

	try:
		user_id, hmac = serializer.loads(token,
		                                 max_age=app.config['MAX_COOKIE_AGE'])
		user = User.query.get(user_id)
		if user and user.hmac == hmac:
			return user
	except:
		pass

	return None



class After(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	start = db.Column(db.DateTime)
	end = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def start_now(self):
		"""Start the after at the current moment"""
		self.start = datetime.utcnow()

	def end_now(self):
		"""End the after at the current moment"""
		self.end = datetime.utcnow()

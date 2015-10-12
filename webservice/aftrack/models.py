from aftrack import app, db, login_manager
from flask.ext.login import make_secure_token
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimedSerializer
from datetime import timedelta

PASSWORD_HASH_LEN = 66 # Based on generate_password_hash output

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(16), unique=True)
	password = db.Column(db.String(66))
	fullname = db.Column(db.String(32))
	yearbook = db.Column(db.Integer)
	admin = db.Column(db.Boolean, default=False) 
	afters = db.relationship('After', backref='user')

	@property
	def hmac(self):
		return make_secure_token(self.username, self.password)

	def get_auth_token(self):
		serializer = TimedSerializer(app.secret_key)
		data = (self.id, self.hmac)
		return serializer.dumps(data)


# TODO test
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
	date = db.Column(db.Date)
	start = db.Column(db.Time)
	end = db.Column(db.Time)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


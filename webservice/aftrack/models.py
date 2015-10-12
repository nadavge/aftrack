from aftrack import db
from werkzeug.security import check_password_hash, generate_password_hash

PASSWORD_HASH_LEN = 66 # Based on generate_password_hash output


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(16), unique=True)
	password = db.Column(db.String(66))
	fullname = db.Column(db.String(32))
	yearbook = db.Column(db.Integer)
	admin = db.Column(db.Boolean, default=False) 
	afters = db.relationship('After', backref='user')


class After(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date)
	start = db.Column(db.Time)
	end = db.Column(db.Time)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

from flask import session, request, abort
from aftrack import app
from itsdangerous import TimedSerializer, SignatureExpired, base64_encode, base64_decode
import string
import random

def generate_signup_token(period, yearbook):
	"""Generate a signup token for a given period in seconds, for
	the given yearbook"""
	serializer = TimedSerializer(app.secret_key)

	data = (period, yearbook)
	return base64_encode(serializer.dumps(data)).decode('utf-8')

def parse_signup_token(token):
	"""Parse the signup token. If valid, return true and the yearbook,
	otherwise return false and the error message"""
	serializer = TimedSerializer(app.secret_key)

	try:
		serial = base64_decode(token)
		period = serializer.loads(serial)[0]

		yearbook = serializer.loads(serial, max_age=period)[1]
		return True, yearbook
	except SignatureExpired:
		return False, 'Token expired'
	except:
		return False, 'Invalid token'

def generate_csrf_token():
	letters = string.ascii_uppercase + string.ascii_lowercase + string.digits

	if '_csrf_token' not in session:
		session['_csrf_token'] = ''.join(random.SystemRandom().choice(letters) for _ in range(64))
	return session['_csrf_token']


def csrf_required(f):
	"""A csrf token wrapper to require the check for a csrf token"""
	def wrapper(*args, **kwargs):
		if request.method == 'POST':
			""" TODO Fix for a pop instead of a get. get is used to allow multiple
			ajax requests consequentivly """
			token = session.get('_csrf_token', None)
			if not token or token != request.form.get('_csrf_token'):
				abort(400)

		return f(*args, **kwargs)

	return wrapper

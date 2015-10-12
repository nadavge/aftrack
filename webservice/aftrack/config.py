import sys
import os
from datetime import timedelta

SECRET_KEY_LEN = 24
SECRET_KEY_FILE = 'secret_key'
# TODO remove after deployment in case of other database
BASEDIR = os.path.abspath(os.path.dirname(__file__))

def create_key_file():
	""" Creates a key file for session handling.
	The key file is stored in SECRET_KEY_FILE, and constitues of
	SECRET_KEY_LEN bytes """
	
	try:
		with open(SECRET_KEY_FILE, 'wb') as secret_key_file:
			secret_key_file.write(os.urandom(SECRET_KEY_LEN))
			print('\'%s\' created successfully!'%SECRET_KEY_FILE)
	except IOError:
		print('Unable to create \'%s\', exiting!'%SECRET_KEY_FILE)
		sys.exit(1)


class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True
	MAX_COOKIE_AGE = timedelta(days=30).total_seconds()
	# TODO remove after deployment in case of other database
	SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASEDIR, 'aftrack.db'))  
	 
	def __init__(self):
		try:
			with open(SECRET_KEY_FILE, 'rb') as secret_key_file:
				self.SECRET_KEY = secret_key_file.read()
		except IOError:
			print('No \'%s\' file, creating one now...'%SECRET_KEY_FILE)
			create_key_file()


class ProductionConfig(Config):
	DEBUG = False


class StagingConfig(Config):
	DEVELOPMENT = True
	DEBUG = True


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True


class TestingConfig(Config):
	TESTING = True


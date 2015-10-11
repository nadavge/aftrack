import sys
import os

SECRET_KEY_LEN = 24
SECRET_KEY_FILE = 'secret_key'

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


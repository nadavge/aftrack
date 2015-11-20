from aftrack import app
from itsdangerous import TimedSerializer, base64_encode

def generate_signup_token(period, yearbook):
	serializer = TimedSerializer(app.secret_key)

	data = (period, yearbook)
	return base64_encode(serializer.dumps(data)).decode('utf-8')


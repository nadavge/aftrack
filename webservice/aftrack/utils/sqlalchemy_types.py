from sqlalchemy import types
import pytz

class TimezoneType(types.TypeDecorator):
	"""Timezone saved as string on the way in, pytz.timezone
	on the way out. (Based on implementation by Konsta Vesterinen)"""

	impl = types.Unicode(50)

	def process_bind_param(self, value, dialect):
		"""Convert the timezone to string"""
		return str(value) if value else None

	def process_result_value(self, value, dialect):
		"""Convert string to timezone pytz"""
		return pytz.timezone(value) if value else None


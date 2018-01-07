import dateutil.parser
from datetime import datetime, date, tzinfo, timedelta
import pytz

class DateMaker():

	def __init__(self):
		pass

	def localize(self, datetime_obj, timezone):
		timezone = pytz.timezone(timezone)
		return timezone.localize(datetime_obj)

	def today(self,timezone):
		# Localize to UTC
		today = datetime.today()
		return self.localize(today, timezone)

	def get_khan_date_format(self,datetime_obj):
		khan_fmt = '%Y-%m-%dT%H:%M:%SZ'
		return datetime_obj.strftime(khan_fmt)

	def offset_to_central(self,datetime_obj):
		utc_offset = timedelta(hours=6)
		return datetime_obj + utc_offset

	def get_today_start_end(self):
		today = self.today("UTC")
		# Get start and end range
		today_start = today.replace(hour=0, minute=0, second=0)
		today_end = today.replace(hour=23, minute=59, second=59)

		# Khan api in UTC, so add 6 hours to the start time
		# We want to track stuff that happened from 6 am UST to
		# 5:59:59 am UST the next day
		delta = timedelta(hours=6)
		today_start += delta
		today_end += delta

		# Get the string formats
		today_start_str = self.get_khan_date_format(today_start)
		today_end_str = self.get_khan_date_format(today_end)
		return [today_start_str, today_end_str]

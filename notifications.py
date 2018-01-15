import boto3
from botocore.exceptions import ClientError
import utils
import traceback
import logging
import file_handler as fh

LOGGER = logging.getLogger(__name__)

class Notifications():

	def __init__(self):
		self.AWS_REGION = "us-east-1"
		self.CHARSET = "UTF-8"
		self.credentials = fh.get_credentials()

	def send_student_text(self, message):
		try:
			if isinstance(self.credentials[fh.STUDENT_NUMBER], list):
				for number in self.credentials[fh.STUDENT_NUMBER]:
					self.send_text(number, message=message)
			else:
				self.send_text(self.credentials[fh.STUDENT_NUMBER], message=message)
		except:
			utils.log_exception(LOGGER)

	def send_parent_text(self, message):
		try:
			if isinstance(self.credentials[fh.PARENT_NUMBER], list):
				for number in self.credentials[fh.PARENT_NUMBER]:
					self.send_text(number, message=message)
			else:
				self.send_text(self.credentials[fh.PARENT_NUMBER], message=message)
		except:
			utils.log_exception(LOGGER)

	def send_text(self, number, message):
		client = boto3.client('sns',region_name=self.AWS_REGION)
		try:
			client.publish(
				PhoneNumber=number,
				Message=message
			)
			LOGGER.info('Text sent to {}!'.format(number));
			print('Text sent to {}'.format(number));
		except:
			utils.log_exception(LOGGER)

	def send_student_email(self, subject, html, body_text=''):
		if not self.credentials or fh.STUDENT_NUMBER not in self.credentials:
			return
		self.send_email(subject, html, body_text, self.credentials[fh.STUDENT_NUMBER])

	def send_parent_email(self, subject, html , body_text): 
		if not self.credentials or fh.PARENT_NUMBER not in self.credentials:
			return
		self.send_email(subject, html, body_text, self.credentials[fh.PARENT_NUMBER])

	def send_email(self, subject, html, body_text='', recipient=None):
		# Reading credentials file could fail
		# And these keys are optional
		if not self.credentials or fh.SENDER not in self.credentials:
			return;
		
		sender = self.credentials[fh.SENDER]
		recipient = recipient or self.credentials[fh.ADMIN]

		body_html = """
		<html>
			<head></head>
			<body>
  				""" + html + """
			</body>
		</html>
		"""  
		if isinstance(recipient, list):
			for number in recipient:
				self._send_email_helper(subject, html, body_text, sender, number)
		else:
			self._send_email_helper(subject, html, body_text, sender, recipient)

	def _send_email_helper(self, subject, html, body_text, sender, recipient):
		client = boto3.client('ses', region_name=self.AWS_REGION)
		try:
			#Provide the contents of the email.
			
			response = client.send_email(
				Destination={
					'ToAddresses': [
						recipient,
					],
				},
				Message={
					'Body': {
						'Html': {
							'Charset': self.CHARSET,
							'Data': html,
						},
						'Text': {
							'Charset': self.CHARSET,
							'Data': body_text,
						},
					},
					'Subject': {
						'Charset': self.CHARSET,
						'Data': subject,
					},
				},
				Source=sender,
			)
			
		# Display an error if something goes wrong.	
		except ClientError as e:
			print(traceback.format_exc())
			LOGGER.exception('Exception')
			print(e.response['Error']['Message'])
		else:
			print("Email sent! Message ID:"),
			print(response['ResponseMetadata']['RequestId'])
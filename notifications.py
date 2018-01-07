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
		pass

	def send_student_text(self, message):
		try:
			self.send_text(self.credentials['student_number'], message=message)
		except:
			utils.log_exception(LOGGER)

	def send_parent_text(self, message):
		try:
			self.send_text(self.credentials['parent_number'], message=message)
		except:
			utils.log_exception(LOGGER)

	def send_text(self, number, message):
		client = boto3.client('sns',region_name=self.AWS_REGION)
		try:
			client.publish(
				PhoneNumber=number,
				Message=message
			)
			pass
		except:
			utils.log_exception(LOGGER)


	def send_error_email(self, subject, html, body_text=''):
		client = boto3.client('ses', region_name=self.AWS_REGION)
		# Reading credentials file could fail
		# And these keys are optional
		if not self.credentials or 'recipient' not in self.credentials or 'sender' not in self.credentials:
			return;
		
		recipient = self.credentials['recipient']
		sender = self.credentials['sender']

		body_html = """
		<html>
			<head></head>
			<body>
  				""" + html + """
			</body>
		</html>
		"""  
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
							'Data': body_html,
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
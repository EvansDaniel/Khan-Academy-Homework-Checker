import socket
import traceback
import notifications
import sys

# Has race condition for now
def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

def log_exception(logger):
	logger.exception('exception')
	print(traceback.format_exc())
	notif = notifications.Notifications()
	notif.send_error_email(subject='Error with Homeworkchecker',
		html='<p>' + traceback.format_exc() + '</p>',
		body_text=traceback.format_exc()
	)
	# For any exception that uses this method, the application 
	# is unable to continue, so exit
	sys.exit(1)

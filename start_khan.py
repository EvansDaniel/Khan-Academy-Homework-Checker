import notifications
import logging

logging.basicConfig(format='%(name)s:%(asctime)s:%(message)s', filename='homeworkchecker.log',level=logging.DEBUG)

notif = notifications.Notifications()

#notif.send_student_text(message='It\'s time to start your khan academy! :) You have 20 problems to do correctly and an hour of videos to watch')
notif.send_parent_text(message='My message')
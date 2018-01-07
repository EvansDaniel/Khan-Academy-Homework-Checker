import time
import sys
import datemaker
import multiprocessing as mp
import auth
import api
from datetime import datetime, date, tzinfo, timedelta
import pytz
import dateutil.parser
import json
import traceback
import notifications
import logging
import utils

LOGGER = logging.getLogger(__name__)

def pretty_print(json_like_data):
    print(json.dumps(json_like_data, indent=4, sort_keys=True))

class VideoChecker():

    # Default to 60 minutes of video watching
    def __init__(self, khan_api_session, minutes_watched_threshold=60):
        self.minutes_watched_threshold = minutes_watched_threshold
        self.khan_api_session = khan_api_session

        self.minutes_watched = self._get_total_min_watched()

    def get_videos_info(self):
        date_maker = datemaker.DateMaker()
        today_start, today_end = date_maker.get_today_start_end()
        user_videos_dict = None
        try:
            user_videos_dict = self.khan_api_session.get_user_progress({
                "dt_start": today_start,
                "dt_end": today_end
            })
        except: 
            utils.log_exception(LOGGER)
        return user_videos_dict

    def _get_total_min_watched(self):
        user_videos = self.get_videos_info()
        minutes_watched = 0
        try:
            minutes_watched = user_videos['students'][0]['videoMinutes']
        except:
            utils.log_exception(LOGGER)

        print('total min watched', minutes_watched)
        return minutes_watched

    def minutes_left(self):
        min_left = self.minutes_watched_threshold - self.minutes_watched
        if min_left < 0:
            return 0
        return min_left

    def has_watched_videos(self):
        return self.minutes_watched >= self.minutes_watched_threshold


# Possibly do something with the "prerequisites" key
class ExcerciseChecker():

    def __init__(self, khan_api_session, num_problems_correct=10):
        self.khan_api_session = khan_api_session
        self.date_maker = datemaker.DateMaker()
        self.todays_exercises = self._get_todays_exercises()
        self.num_problems_correct = num_problems_correct

    def _get_todays_exercises(self):
        date_maker = datemaker.DateMaker()
        today_start, today_end = date_maker.get_today_start_end()
        try: 
            todays_exercises = self.khan_api_session.get_user_focus(params={
                "dt_start":today_start,
                "dt_end":today_end
            })
            todays_exercises = todays_exercises['context']['dict_exercise_seconds']
        except:
            utils.log_exception(LOGGER)
        return todays_exercises

    def get_num_problems_correct_today(self):
        total_correct = 0
        try:
            for key, value in self.todays_exercises.items():
                total_correct += value['correct']
        except:
            utils.log_exception(LOGGER)

        return total_correct

    def problems_correct_left(self):
        correct_left = self.num_problems_correct - self.get_num_problems_correct_today()
        if correct_left < 0:
            return 0
        return correct_left

    def made_progress(self,):
        #self.stored_exercises.add_exercises(self.todays_exercises)
        num_problems_correct_today = self.get_num_problems_correct_today()
        print('num problems correct today', num_problems_correct_today)
        return num_problems_correct_today >= self.num_problems_correct

def build_not_done_message(video_checker, exercise_checker):
    video_stats = 'https://www.khanacademy.org/profile/sarahleeannpate/vital-statistics/videos'
    exercise_stats = 'https://www.khanacademy.org/profile/sarahleeannpate/vital-statistics/focus'
    return 'You have ' + str(round(video_checker.minutes_left())) + ' minutes left of videos to watch and ' + \
    str(exercise_checker.problems_correct_left()) + ' problems left to get correct on the first try. ' + \
    'Go to '+ video_stats + ' and ' + exercise_stats + ' to track your progress.'

def check_homework():
    PROBLEMS_CORRECT = 20
    MINUTES_WATCHED_THRESHOLD = 60
    session = auth.authenticate()

    # Repeatedly prompt user for a resource and make authenticated API calls.
    if session is None:
        print('Failed to authenticate. Invalid session retreived')
        LOGGER.error('Failed to authenticate session')
        notif = notifications.Notifications()
        notif.send_error_email(subject='Error with Homeworkchecker',
            html='<p> Failed to authenticate session </p>',
            body_text='Failed to authenticate session'
        )
        return;

    khan_api = api.Api(session)
    
    video_checker = VideoChecker(khan_api, minutes_watched_threshold=MINUTES_WATCHED_THRESHOLD)
    exercise_checker = ExcerciseChecker(khan_api, num_problems_correct=PROBLEMS_CORRECT)
    if exercise_checker.made_progress() and video_checker.has_watched_videos():
        # Tell Sarah good job?
        # And mom that Sarah has completed it?
        pass
    else:
        notif = notifications.Notifications()
        video_stats = 'https://www.khanacademy.org/profile/sarahleeannpate/vital-statistics/videos'
        exercise_stats = 'https://www.khanacademy.org/profile/sarahleeannpate/vital-statistics/focus'
        student_msg = 'You have not completed your khan academy yet. You have {} minutes of videos '.format(round(video_checker.minutes_left())) + \
         'left and {} problems left to answer correctly.'.format(exercise_checker.problems_correct_left()) + \
         ' You can track your progress by visiting these pages (you must be logged in) and viewing today\'s activity: {} and {}'.format(video_stats, exercise_stats)
        parent_msg = 'Sarah hasn\'t completed her khan academy yet. She has {} minutes of videos left to watch'.format(round(video_checker.minutes_left())) + \
        ' and {} problems left to answer correctly.'.format(exercise_checker.problems_correct_left()) + \
        ' You can learn more about what Sarah has been working on by visiting these pages (you must be logged in) and viewing today\'s activity: {} and {}'.format(video_stats, exercise_stats)
        notif.send_parent_text(message=parent_msg)
        notif.send_student_text(message=student_msg)

def main():
    logging.basicConfig(format='%(name)s:%(asctime)s:%(message)s', filename='homeworkchecker.log',level=logging.DEBUG)
    check_homework()

if __name__ == "__main__":
    main()
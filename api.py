import logging
import utils

DEFAULT_API_RESOURCE = '/api/v1/user'
SERVER_URL = 'http://www.khanacademy.org'



LOGGER = logging.getLogger(__name__)


class Api():

    def __init__(self, session):
        self.session = session
        self.user = self.get_user()
        self.kaid = self.user['kaid']
        self.student_key = self.user['student_summary']['key']

    def get_user(self, params={}):
        response = self.get_response('/api/v1/user', params)
        return response and response.json()

    # Params: dt_start, dt_end
    # Unstable internal api
    def get_user_focus(self, params={}):
        response = self.get_response('/api/internal/user/'+ self.student_key + '/focus', params)
        return response and response.json()        

    def get_user_videos(self, params={}):
        response = self.get_response('/api/v1/user/videos', params)
        return response and response.json()

    def get_user_exercies(self, params={}):
        response = self.get_response('/api/v1/user/exercises', params)
        return response and response.json()   

    # Params: dt_start, dt_end
    # Unstable internal api
    def get_user_progress(self, params={}):
        response = self.get_response('/api/internal/user/' + self.kaid + '/progress', params)
        return response and response.json()

    def get_response(self, url, params={}):
        try:
            url = self.get_url(url)
            print('GET', url)
            response = self.session.get(url, params=params)
        except:
            utils.log_exception(LOGGER)
        return response

    def get_url(self, resource_url):
        return SERVER_URL + resource_url

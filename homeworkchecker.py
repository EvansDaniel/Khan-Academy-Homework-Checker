import cgi
import rauth
import http.server
import socketserver
import time
import webbrowser
from time import sleep
from selenium import webdriver
import json
import cgi
import os.path 
import http.server
import socketserver
from selenium.webdriver.chrome.options import Options

import shared_constants

print(shared_constants.VERIFIER_FILE)

CALLBACK_BASE = '127.0.0.1'
VERIFIER = None
AUTH_TOKEN_FILE='auth_tokens.json'
CONSUMER_KEY = 'gMCe7huanHVnBdvW'
CONSUMER_SECRET = 'hm7GXAVKytnQp4V2'
SERVER_URL = 'http://www.khanacademy.org'
DEFAULT_API_RESOURCE = '/api/v1/playlists'
VERIFIER = None
CREDENTIALS_FILE='.credentials.json'

# Make an authenticated API call using the given rauth session.
def get_api_resource(session):
    resource_url = input("Resource relative url (e.g. %s): " %
        DEFAULT_API_RESOURCE) or DEFAULT_API_RESOURCE

    url = SERVER_URL + resource_url
    split_url = url.split('?', 1)
    params = {}

    # Separate out the URL's parameters, if applicable.
    if len(split_url) == 2:
        url = split_url[0]
        params = cgi.parse_qs(split_url[1], keep_blank_values=False)

    start = time.time()
    response = session.get(url, params=params)
    end = time.time()

    print("\n")
    print(response.text)
    print("\nTime: %ss\n" % (end - start))

def get_email_password_from_credentials():
    # TODO: check if the file exists and that it is valid JSON
    with open(CREDENTIALS_FILE, 'r') as file:
        data = json.load(file)
        if 'email' in data and 'pass' in data:
            return [data['email'], data['pass']]
        else:
            print('Invalid credentials json: no pass or email key')
            return [None,None]

def authorize_url_sign_in(authorize_url):
    kaEmail_S = 'input[type=text]'
    kaPass_S = 'input[type=password]'
    kaLoginButton_S = '.button_1ilkz0g-o_O-common_hqgk90-o_O-large_10vyrhl-o_O-all_tca0ge'

    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # Call oauth with authorize url
    driver.get(authorize_url)
    email, password = get_email_password_from_credentials()
    # TODO: do more than print in this case 
    if email == None or password == None:
        print('No email or password stored')
    driver.find_element_by_css_selector(kaEmail_S).send_keys(email)
    driver.find_element_by_css_selector(kaPass_S).send_keys(password)
    driver.find_element_by_css_selector(kaLoginButton_S).click()
    sleep(5)
    # Accept oauth button
    #driver.execute_script('document.querySelector(\'a\').click()')
    driver.find_element_by_css_selector('a').click()

def write_auth_tokens(request_token, secret_request_token, VERIFIER):
    with open(AUTH_TOKEN_FILE, 'w') as outfile:
        json.dump({
            "request_token":request_token,
            "secret_request_token":secret_request_token,
            "VERIFIER":VERIFIER
        }, outfile)

def num_videos_watched(request_token, secret_request_token, VERIFIER):
    pass

def auth_tokens_expired():
    return True

def get_verifier_token(VERIFIER_FILE):
    with open(VERIFIER_FILE, 'r') as file:
        data = json.load(file)
        return data['VERIFIER']

def run_tests():
    global CONSUMER_KEY, CONSUMER_SECRET, SERVER_URL
    service = rauth.OAuth1Service(
           name='test',
           consumer_key=CONSUMER_KEY,
           consumer_secret=CONSUMER_SECRET,
           request_token_url=SERVER_URL + '/api/auth2/request_token',
           access_token_url=SERVER_URL + '/api/auth2/access_token',
           authorize_url=SERVER_URL + '/api/auth2/authorize',
           base_url=SERVER_URL + '/api/auth2')

    auth_token_file_exists = lambda: os.path.isfile(AUTH_TOKEN_FILE)

    session = None
    if auth_token_file_exists() and not auth_tokens_expired():
        print('here')
        data = json.load(open(AUTH_TOKEN_FILE))
        request_token = data['request_token'] 
        secret_request_token = data['secret_request_token']
        VERIFIER = data['VERIFIER']
        # TODO: check if tokens are valid
        print(request_token, secret_request_token, VERIFIER)
        session = service.get_auth_session(request_token, secret_request_token,
            params={
                'oauth_verifier': VERIFIER
            })
    else: 
        CONSUMER_KEY = CONSUMER_KEY or input("consumer key: ")
        CONSUMER_SECRET = CONSUMER_SECRET or input("consumer secret: ")
        SERVER_URL = SERVER_URL or input("server base url: ")

        # Create an OAuth1Service using rauth.
        request_token, secret_request_token = service.get_request_token(
            params={'oauth_callback': 'http://%s:8000/' %
                (CALLBACK_BASE)})
        
        authorize_url = service.get_authorize_url(request_token)
        # Uncomment for manual authorization
        # webbrowser.open(authorize_url)
        authorize_url_sign_in(authorize_url)
        print('Waiting for server to respond and write verifier file ')

        sleep(5)

        VERIFIER = get_verifier_token(shared_constants.VERIFIER_FILE)

        print('VERIFIER', VERIFIER)
        print('request_token', request_token)
        print('secret_request_token', secret_request_token)

        write_auth_tokens(request_token, secret_request_token, VERIFIER)

        params = {
            'oauth_verifier': VERIFIER
        }
        session = service.get_auth_session(request_token, secret_request_token,
            params=params)

        # Repeatedly prompt user for a resource and make authenticated API calls.
        while(True):
            get_api_resource(session)


def main():
    run_tests()

if __name__ == "__main__":
    main()
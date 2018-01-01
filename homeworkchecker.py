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

CALLBACK_BASE = '127.0.0.1'
VERIFIER = None
AUTH_TOKEN_FILE='auth_tokens.json'
CONSUMER_KEY = 'gMCe7huanHVnBdvW'
CONSUMER_SECRET = 'hm7GXAVKytnQp4V2'
SERVER_URL = 'http://www.khanacademy.org'
DEFAULT_API_RESOURCE = '/api/v1/user'
VERIFIER = None
CREDENTIALS_FILE='.credentials.json'
TOKEN_TEST_URL = '/api/v1/playlists'

# Make an authenticated API call using the given rauth session.
def get_api_resource(session, params={}, resource=DEFAULT_API_RESOURCE):
    resource_url = resource or input("Resource relative url (e.g. %s): " %
        DEFAULT_API_RESOURCE)

    url = SERVER_URL + resource_url
    split_url = url.split('?', 1)

    # Separate out the URL's parameters, if applicable.
    if len(split_url) == 2:
        url = split_url[0]
        params = cgi.parse_qs(split_url[1], keep_blank_values=False)

    start = time.time()
    response = session.get(url, params=params)
    end = time.time()

    #print("\n")
    #print(response.text)
    #print("\nTime: %ss\n" % (end - start))
    return response and response.json()

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
    print('Running headless browser to log in')
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
    driver.find_element_by_css_selector('a').click()
    print('Successful login')

def write_auth_tokens(request_token, secret_request_token, VERIFIER):
    with open(AUTH_TOKEN_FILE, 'w') as outfile:
        json.dump({
            "request_token":request_token,
            "secret_request_token":secret_request_token,
            "VERIFIER":VERIFIER
        }, outfile)
        print('Renewed auth tokens written')

def num_videos_watched(request_token, secret_request_token, VERIFIER):
    pass

def auth_tokens_expired(session):
    print('checking auth tokens expiration...')
    is_expired = get_api_resource(session, resource='/api/v1/user') == None
    return is_expired


def get_verifier_token(VERIFIER_FILE):
    with open(VERIFIER_FILE, 'r') as file:
        data = json.load(file)
        if 'VERIFIER' not in data:
            print('VERIFIER key not in', VERIFIER_FILE, 'json')
        print('VERIFIER token received')
        return data['VERIFIER']


def renew_tokens(service):
    global CONSUMER_KEY, CONSUMER_SECRET, SERVER_URL
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
    print('Session retrived from renewed tokens')

    return session

def authenticate():
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
    # Check if we have tokens that aren't expired
    if auth_token_file_exists():
        print('Found cached auth tokens') 
        try:
            data = json.load(open(AUTH_TOKEN_FILE))
            request_token = data['request_token'] # <---------------------- NOT Invalid auth token here
            secret_request_token = data['secret_request_token']
            VERIFIER = data['VERIFIER']
            session = service.get_auth_session(request_token, secret_request_token,
                    params={
                        'oauth_verifier': VERIFIER
                    })
            if not auth_tokens_expired(session):
                print('Auth tokens valid')
                return session
            else:
                print('Auth tokens invalid. Renewing and recaching...')
                session = renew_tokens(service)
        except:
            print('A problem occured using cached auth tokens. Renewing and recaching...')
            session = renew_tokens(service)

    print('Done')
    return session


def check_homework():
    session = authenticate()

    # Repeatedly prompt user for a resource and make authenticated API calls.
    if session is None:
        print('Failed to authenticate')
        return;

    while(True):
        print(get_api_resource(session, resource=None))


def main():
    check_homework()

if __name__ == "__main__":
    main()
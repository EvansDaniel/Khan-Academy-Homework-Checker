import rauth
import http.server
import socketserver
import time
import webbrowser
from time import sleep
from selenium import webdriver
import json
import socket
import os.path 
import os
from selenium.webdriver.chrome.options import Options
import subprocess
import sys
import cgi
import multiprocessing as mp
import json

AUTH_TOKEN_FILE='auth_tokens.json'
# TODO add consumer key and consumer secret to credentials.json
CONSUMER_KEY = 'gMCe7huanHVnBdvW'
CONSUMER_SECRET = 'hm7GXAVKytnQp4V2'
SERVER_URL = 'http://www.khanacademy.org'
TOKEN_TEST_URL = '/api/v1/user'
DEFAULT_API_RESOURCE = TOKEN_TEST_URL

CREDENTIALS_FILE='.credentials.json'
CREDENTIAL_EMAIL_KEY = 'email'
CREDENTIAL_PASSWORD_KEY = 'password'
CREDENTIAL_CONSUMER_KEY = 'consumer_key'
CREDENTIAL_CONSUMER_SECRET_KEY = 'consumer_secret'

CALLBACK_BASE = '127.0.0.1'
VERIFIER = None
OAUTH_VERIFIER_KEY = 'oauth_verifier'
VERIFIER_FILE = 'verifier.json'
PORT = 8000
SERVER_PROCESS = None


def write_verifier(VERIFIER):
    with open(VERIFIER_FILE, 'w') as outfile:
        json.dump({
            "VERIFIER":VERIFIER
        }, outfile)

# Create the callback server that's used to set the oauth verifier after the
# request token is authorized.
def create_callback_server(port):
    class CallbackHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            global VERIFIER
            
            #print('path',self.path)
            if len(self.path.split('?', 1)) == 2:

                params = cgi.parse_qs(self.path.split('?', 1)[1],
                    keep_blank_values=False)

                #print('params',params)

                # Make sure correct query paramters are in url
                if OAUTH_VERIFIER_KEY in params and len(params[OAUTH_VERIFIER_KEY]) >= 1:
                    VERIFIER = params[OAUTH_VERIFIER_KEY][0]

                    print('Server writing verifier file')
                    write_verifier(VERIFIER)

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes("You can now close this window", "utf-8"))
                else:
                    print('Given invalid oauth path/query params ->', 'path', self.path, 'params', params)
            else:
                print('Received invalid path', self.path)

    server = socketserver.TCPServer((CALLBACK_BASE, port), CallbackHandler)
    return server

# Make an authenticated API call using the given rauth session.
def get_api_resource(session, params={}, resource=DEFAULT_API_RESOURCE):
    # TODO: remove input stuff
    resource_url = resource or input("Resource relative url (e.g. %s): " %
        DEFAULT_API_RESOURCE)

    if not resource_url:
        resource_url = DEFAULT_API_RESOURCE

    url = SERVER_URL + resource_url
    split_url = url.split('?', 1)

    # Separate out the URL's parameters, if applicable.
    if len(split_url) == 2:
        url = split_url[0]
        params = cgi.parse_qs(split_url[1], keep_blank_values=False)

    #start = time.time()
    response = session.get(url, params=params)
    #end = time.time()

    return response and response.json()

def get_credentials():
    if os.path.isfile(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                data = json.load(file)
                if CREDENTIAL_EMAIL_KEY in data and CREDENTIAL_PASSWORD_KEY in data and CREDENTIAL_CONSUMER_KEY in data and CREDENTIAL_CONSUMER_SECRET_KEY in data: 
                    return data
                else:
                    print('Invalid keys in %s. Need %s, %s, %s, and %s' 
                        % (CREDENTIALS_FILE, CREDENTIAL_EMAIL_KEY, CREDENTIAL_PASSWORD_KEY, CREDENTIAL_CONSUMER_KEY, CREDENTIAL_CONSUMER_SECRET_KEY))
                    print('See README.md for necessary credentials')
                    return None
            except:
                print('Invalid %s. Must provide that file with valid keys' 
                    % (CREDENTIALS_FILE))
                print('See README.md for necessary credentials')
                return None
    else:
        print('No %s provided' % (CREDENTIALS_FILE))
        return None

def authorize_url_sign_in(authorize_url, server_process, credentials_dict):
    print('Running headless browser to log in')
    kaEmail_S = 'input[type=text]'
    kaPass_S = 'input[type=password]'
    kaLoginButton_S = '.button_1ilkz0g-o_O-common_hqgk90-o_O-large_10vyrhl-o_O-all_tca0ge'

    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # Call oauth with authorize url
    driver.get(authorize_url)
    print('Getting authorize url')

    print('Sending credential info')
    driver.find_element_by_css_selector(kaEmail_S).send_keys(credentials_dict[CREDENTIAL_EMAIL_KEY])
    driver.find_element_by_css_selector(kaPass_S).send_keys(credentials_dict[CREDENTIAL_PASSWORD_KEY])
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
        print('Renewed auth tokens cached')

def num_videos_watched(request_token, secret_request_token, VERIFIER):
    pass

def auth_tokens_expired(session):
    print('checking auth tokens expiration...')
    is_expired = get_api_resource(session, resource=TOKEN_TEST_URL) == None
    return is_expired


def get_verifier_token(VERIFIER_FILE):
    if os.path.isfile(VERIFIER_FILE):
        with open(VERIFIER_FILE, 'r') as file:
            data = json.load(file)
            if 'VERIFIER' not in data:
                print('VERIFIER key not in', VERIFIER_FILE, 'json')
            print('VERIFIER token received')
            return data['VERIFIER']
    else:
        print('File does not exist')
        return None

def start_server(port):
    print('Starting server')
    callback_server = create_callback_server(port)
    print('Server %s listening on %s'% (CALLBACK_BASE, port))
    callback_server.serve_forever()

# Has race condition for now
def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

def renew_tokens(service):
    credentials_dict = get_credentials()
    if credentials_dict is None:
        print('No improper credentials from %s. Exiting...' % (CREDENTIALS_FILE))
        server_process.terminate()
        sys.exit(1)

    global CONSUMER_KEY, CONSUMER_SECRET, SERVER_URL, VERIFIER
    CONSUMER_KEY = credentials_dict[CREDENTIAL_CONSUMER_KEY]
    CONSUMER_SECRET = credentials_dict[CREDENTIAL_CONSUMER_SECRET_KEY]

    if os.path.isfile(AUTH_TOKEN_FILE):
        os.remove(AUTH_TOKEN_FILE)
    # Remove files so we can wait for server to create verifier file
    # without race condition
    if os.path.isfile(VERIFIER_FILE):
        os.remove(VERIFIER_FILE)

    port = get_free_tcp_port()
    SERVER_PROCESS = mp.Process(target=start_server, args=(port,))
    SERVER_PROCESS.start()

    # Create an OAuth1Service using rauth.
    request_token, secret_request_token = service.get_request_token(
        params={'oauth_callback': 'http://%s:%d/' %
            (CALLBACK_BASE, port)})
    
    authorize_url = service.get_authorize_url(request_token)
    # Uncomment for manual authorization
    # webbrowser.open(authorize_url)
    authorize_url_sign_in(authorize_url, SERVER_PROCESS, credentials_dict)
    print('Waiting for server to respond and write verifier file ')

    tries = 0
    while(VERIFIER == None and tries < 20):
        VERIFIER = get_verifier_token(VERIFIER_FILE)
        tries += 1
        sleep(1)

    print('VERIFIER', VERIFIER)
    print('request_token', request_token)
    print('secret_request_token', secret_request_token)

    write_auth_tokens(request_token, secret_request_token, VERIFIER)

    params = {
        OAUTH_VERIFIER_KEY: VERIFIER
    }
    session = service.get_auth_session(request_token, secret_request_token,
        params=params)
    print('Session retrieved from renewed tokens')
    # End the server process
    SERVER_PROCESS.terminate()

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
                        OAUTH_VERIFIER_KEY: VERIFIER
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
            pass
    else:
        print('No', AUTH_TOKEN_FILE, 'found')
        session = renew_tokens(service)
    print('Done')
    return session


def check_homework():
    session = authenticate()

    # Repeatedly prompt user for a resource and make authenticated API calls.
    if session is None:
        print('Failed to authenticate. Invalid session retreived')
        return;

    while(True):
        print(get_api_resource(session, resource=None))


def main():
    check_homework()

if __name__ == "__main__":
    main()
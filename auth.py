from selenium import webdriver
import rauth
import webbrowser
from selenium.webdriver.chrome.options import Options
import file_handler as fh
import os
import os.path
import sys
import utils
import multiprocessing as mp
import server
from time import sleep
import api
import logging
import traceback

LOGGER = logging.getLogger(__name__)

def authenticate():

    credentials_dict = fh.get_credentials()
    if credentials_dict is None:
        print('Improper credentials from %s. Exiting...' % (fh.CREDENTIALS_FILE))
        sys.exit(1)

    consumer_key = credentials_dict[fh.CONSUMER_KEY]
    consumer_secret = credentials_dict[fh.CONSUMER_SECRET_KEY]

    service = rauth.OAuth1Service(
           name='test',
           consumer_key=consumer_key,
           consumer_secret=consumer_secret,
           request_token_url=api.SERVER_URL + '/api/auth2/request_token',
           access_token_url=api.SERVER_URL + '/api/auth2/access_token',
           authorize_url=api.SERVER_URL + '/api/auth2/authorize',
           base_url=api.SERVER_URL + '/api/auth2')

    session = None
    # Check if we have tokens that aren't expired
    if fh.auth_token_file_exists():
        print('Found cached auth tokens') 
        try:
            request_token, secret_request_token, verifier = fh.get_auth_tokens()
            session = service.get_auth_session(request_token, secret_request_token,
                    params={
                        server.OAUTH_VERIFIER_KEY: verifier
                    })
            if not auth_tokens_expired(session):
                print('Auth tokens valid')
                return session
            else:
                print('Auth tokens invalid. Renewing and recaching...')
                session = renew_tokens(service, credentials_dict)
        except:
            print('A problem occured using cached auth tokens. Renewing and recaching...')
            print(traceback.format_exc())
            LOGGER.exception('Exception')
            session = renew_tokens(service, credentials_dict)
    else:
        print('No', fh.AUTH_TOKEN_FILE, 'found')
        session = renew_tokens(service,credentials_dict)
    print('Done')
    return session

def authorize_url_sign_in(authorize_url, credentials_dict, server_process):
    driver = None
    try:
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
        driver.find_element_by_css_selector(kaEmail_S).send_keys(credentials_dict[fh.EMAIL_KEY])
        driver.find_element_by_css_selector(kaPass_S).send_keys(credentials_dict[fh.PASSWORD_KEY])
        driver.find_element_by_css_selector(kaLoginButton_S).click()
        # Wait for the "Accept" page to load
        sleep(5)
        # Accept oauth button
        driver.find_element_by_css_selector('a').click()
        print('Successful login')
    except:
        server_process.terminate()
        utils.log_exception(LOGGER)
    finally:
        if driver:
            driver.close()


def start_server(port):
    print('Starting server')
    callback_server = server.create_callback_server(port)
    print('Server %s listening on %s'% (server.CALLBACK_BASE, port))
    callback_server.serve_forever()

def renew_tokens(service, credentials_dict):

    # Remove files so we can wait for server to create verifier file
    # without race condition
    fh.renew_files()

    port = utils.get_free_tcp_port()
    server_process = mp.Process(target=start_server, args=(port,))
    server_process.start()

    # Create an OAuth1Service using rauth.
    request_token, secret_request_token = service.get_request_token(
        params={'oauth_callback': 'http://%s:%d/' %
            (server.CALLBACK_BASE, port)})
    
    authorize_url = service.get_authorize_url(request_token)
    # Uncomment for manual authorization
    # webbrowser.open(authorize_url)
    authorize_url_sign_in(authorize_url, credentials_dict, server_process)
    print('Waiting for server to respond and write verifier file ')

    verifier = fh.get_verifier_token()

    if verifier == None:
        print('Server failed to receive and write verifier file')
        server_process.terminate()
        sys.exit(1)

    print('verifier_token', verifier)
    print('request_token', request_token)
    print('secret_request_token', secret_request_token)

    fh.write_auth_tokens(request_token, secret_request_token, verifier)

    params = {
        server.OAUTH_VERIFIER_KEY: verifier
    }
    session = service.get_auth_session(request_token, secret_request_token,
        params=params)
    print('Session retrieved from renewed tokens')
    # End the server process
    server_process.terminate()

    return session

def auth_tokens_expired(session):
    print('checking auth tokens expiration...')
    khan_api = api.Api(session)
    is_expired = khan_api.get_user() == None
    return is_expired
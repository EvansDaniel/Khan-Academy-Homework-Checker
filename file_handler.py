import json
import os
import os.path
from time import sleep

AUTH_TOKEN_FILE='auth_tokens.json'
VERIFIER_FILE = 'verifier.json'
REQUEST_TOKEN_KEY = 'request_token'
SECRET_REQUEST_TOKEN_KEY = 'secret_request_token'
VERIFIER_KEY = 'verifier'

CREDENTIALS_FILE='.credentials.json'
EMAIL_KEY = 'email'
PASSWORD_KEY = 'password'
CONSUMER_KEY = 'consumer_key'
CONSUMER_SECRET_KEY = 'consumer_secret'
STUDENT_NUMBER = 'student_number'
PARENT_NUMBER = 'parent_number'

def renew_files():
	if os.path.isfile(AUTH_TOKEN_FILE):
		os.remove(AUTH_TOKEN_FILE)

	if os.path.isfile(VERIFIER_FILE):
		os.remove(VERIFIER_FILE)

def write_auth_tokens(request_token, secret_request_token, VERIFIER):
    with open(AUTH_TOKEN_FILE, 'w') as outfile:
        json.dump({
        	REQUEST_TOKEN_KEY: request_token,
            SECRET_REQUEST_TOKEN_KEY: secret_request_token,
            VERIFIER_KEY: VERIFIER
        }, outfile)
        print('Renewed auth tokens cached')

def auth_token_file_exists():
	return os.path.isfile(AUTH_TOKEN_FILE)

def get_auth_tokens():
	data = [None, None, None]
	if os.path.isfile(AUTH_TOKEN_FILE):
		try:
			auth_dict = json.load(open(AUTH_TOKEN_FILE))
			request_token = auth_dict[REQUEST_TOKEN_KEY] 
			secret_request_token = auth_dict[SECRET_REQUEST_TOKEN_KEY]
			verifier = auth_dict[VERIFIER_KEY]
			data = [request_token, secret_request_token, verifier]
		except:
			return data
	return data

def valid_verifier_json(verifier_dict):
	return VERIFIER_KEY in verifier_dict

def get_verifier_token():
	tries = 0
	verifier = None
	while(verifier == None and tries < 20):
		verifier = get_verifier_token_helper(VERIFIER_FILE)
		tries += 1
		sleep(1)
	return verifier

def get_verifier_token_helper(VERIFIER_FILE):
    if os.path.isfile(VERIFIER_FILE):
        with open(VERIFIER_FILE, 'r') as file:
            data = json.load(file)
            if valid_verifier_json(data):
            	print('verifier token received')
            	return data[VERIFIER_KEY]
            else:
            	print('verifier key not in', VERIFIER_FILE, 'json')
            	return None
    else:
        return None


def write_verifier(verifier):
    with open(VERIFIER_FILE, 'w') as outfile:
        json.dump({
            VERIFIER_KEY:verifier
        }, outfile)

def valid_credentials_json(json_dict):
	return EMAIL_KEY in json_dict and \
                STUDENT_NUMBER in json_dict and \
                PARENT_NUMBER in json_dict and \
                PASSWORD_KEY in json_dict and \
                CONSUMER_KEY in json_dict and \
                CONSUMER_SECRET_KEY in json_dict

def get_credentials():
    if os.path.isfile(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                data = json.load(file)
                if valid_credentials_json(data): 
                    return data
                else:
                    print('Invalid keys in %s. Need %s, %s, %s, and %s' 
                        % (CREDENTIALS_FILE, EMAIL_KEY, 
                        	PASSWORD_KEY, 
                        	CONSUMER_KEY, 
                        	CONSUMER_SECRET_KEY, 
                            STUDENT_NUMBER, 
                            PARENT_NUMBER))
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
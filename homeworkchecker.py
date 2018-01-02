import time
import sys
import multiprocessing as mp
import auth
import api

def check_homework():
    session = auth.authenticate()

    # Repeatedly prompt user for a resource and make authenticated API calls.
    if session is None:
        print('Failed to authenticate. Invalid session retreived')
        return;

    while(True):
        print(api.get_api_resource(session, resource=None))


def main():
    check_homework()

if __name__ == "__main__":
    main()
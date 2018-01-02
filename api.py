DEFAULT_API_RESOURCE = '/api/v1/user'
SERVER_URL = 'http://www.khanacademy.org'

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
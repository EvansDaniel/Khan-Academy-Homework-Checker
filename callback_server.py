import cgi
import http.server
import socketserver
import json

import shared_constants

CALLBACK_BASE = '127.0.0.1'
VERIFIER = None
PORT = 8000
OAUTH_VERIFIER_KEY = 'oauth_verifier'


def write_verifier(VERIFIER):
    with open(shared_constants.VERIFIER_FILE, 'w') as outfile:
        json.dump({
            "VERIFIER":VERIFIER
        }, outfile)

# Create the callback server that's used to set the oauth verifier after the
# request token is authorized.
def create_callback_server():
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

                    print('VERIFIER', VERIFIER)
                    write_verifier(VERIFIER)

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes("You can now close this window", "utf-8"))
                else:
                    print('Given invalid oauth path/query params ->', 'path', self.path, 'params', params)
            else:
                print('Received invalid path', self.path)

    server = socketserver.TCPServer((CALLBACK_BASE, PORT), CallbackHandler)
    return server


callback_server = create_callback_server()
print('Listening %s on %s'% (CALLBACK_BASE, PORT))
callback_server.serve_forever()
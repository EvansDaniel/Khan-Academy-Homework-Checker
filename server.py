import cgi
import http.server
import socketserver
import file_handler as fh

CALLBACK_BASE = '127.0.0.1'
OAUTH_VERIFIER_KEY = 'oauth_verifier'

# Create the callback server that's used to set the oauth verifier after the
# request token is authorized.
def create_callback_server(port):
    class CallbackHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if len(self.path.split('?', 1)) == 2:

                params = cgi.parse_qs(self.path.split('?', 1)[1],
                    keep_blank_values=False)

                #print('params',params)

                # Make sure correct query paramters are in url
                if OAUTH_VERIFIER_KEY in params and len(params[OAUTH_VERIFIER_KEY]) >= 1:
                    verifier = params[OAUTH_VERIFIER_KEY][0]

                    print('Server writing verifier file')
                    fh.write_verifier(verifier)

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
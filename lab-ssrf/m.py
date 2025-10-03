from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class InternalService(BaseHTTPRequestHandler):
    """A simple HTTP server representing a sensitive internal service."""
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        # This is the "secret" data an attacker should not see.
        self.wfile.write("<h1>[INTERNAL] Sensitive Data Accessed!</h1>".encode('utf-8'))

def run(server_class=HTTPServer, handler_class=InternalService, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting internal service on http://127.0.0.1:{port}...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping internal service.\n')

if __name__ == '__main__':
    # We will run this on a different port than the main app (e.g., 8000)
    run(port=8000)

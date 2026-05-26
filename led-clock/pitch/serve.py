#!/usr/bin/env python3
import http.server, base64, os, sys

PORT = 8888
USER = "demo"
PASS = "wordclock"
DIR = os.path.dirname(os.path.abspath(__file__))

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIR, **kw)

    def do_GET(self):
        auth = self.headers.get("Authorization")
        expected = "Basic " + base64.b64encode(f"{USER}:{PASS}".encode()).decode()
        if auth != expected:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Presentation"')
            self.end_headers()
            return
        if self.path == "/":
            self.path = "/presentation.html"
        super().do_GET()

print(f"Serving on http://0.0.0.0:{PORT}")
print(f"Login: {USER} / {PASS}")
http.server.HTTPServer(("0.0.0.0", PORT), AuthHandler).serve_forever()

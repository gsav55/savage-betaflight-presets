#!/usr/bin/env python3
"""Serve ONLY preset-source files on loopback; never expose the backup directory."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def allowed(self):
        host = self.headers.get('Host', '')
        if host not in ('127.0.0.1:18765', 'localhost:18765'):
            self.send_error(403, 'Loopback host required')
            return False
        path = PurePosixPath(unquote(urlsplit(self.path).path))
        parts = path.parts
        if '..' in parts:
            self.send_error(403)
            return False
        allowed = str(path) in ('/index.json','/index_hash.txt') or (
            len(parts)>2 and parts[1]=='presets' and path.suffix=='.txt')
        resolved = (ROOT / str(path).lstrip('/')).resolve()
        if not allowed or not resolved.is_relative_to(ROOT) or not resolved.is_file():
            self.send_error(404)
            return False
        return True

    def end_headers(self):
        origin = self.headers.get('Origin','')
        if origin == 'null' or re.fullmatch(r'https://(?:[a-zA-Z0-9-]+\.)?app\.betaflight\.com', origin):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods','GET, HEAD, OPTIONS')
            self.send_header('Access-Control-Allow-Private-Network','true')
            self.send_header('Vary','Origin')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()

    def do_GET(self):
        if self.allowed(): super().do_GET()

    def do_HEAD(self):
        if self.allowed(): super().do_HEAD()

    def do_OPTIONS(self):
        if self.allowed():
            self.send_response(204)
            self.end_headers()

if __name__=='__main__':
    print('Savage presets: http://127.0.0.1:18765/\nKeep this window open while using Presets. Press Control-C to stop.', flush=True)
    try:
        ThreadingHTTPServer(('127.0.0.1',18765),Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nPreset source stopped.')

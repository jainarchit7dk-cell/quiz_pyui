"""Tiny HTTP server: GET -> render the UI. POST -> run handler, change state, re-render."""
import os, secrets, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
from .core import State, render_body, render_page


class App:
    def __init__(self, view, initial_state, title="PyUI App", css=""):
        self.view, self.initial_state = view, initial_state
        self.title, self.css = title, css
        self.sessions, self.lock = {}, threading.Lock()   # one State per browser (cookie)

    def get_state(self, sid):
        if sid not in self.sessions:
            self.sessions[sid] = State(**self.initial_state())
        return self.sessions[sid]

    def page(self, state):
        body, _ = render_body(self.view, state)
        return render_page(body, self.title, self.css)

    def dispatch(self, state, event_id):
        """Event -> handler -> state change. The next GET re-renders the UI."""
        _, handlers = render_body(self.view, state)   # rebuild id -> handler map
        handler = handlers.get(event_id)
        if handler:
            handler(state)

    def run(self, host="0.0.0.0", port=None):
        app = self
        port = port or int(os.environ.get("PORT", 8000))

        class Handler(BaseHTTPRequestHandler):
            def _sid(self):
                for part in self.headers.get("Cookie", "").split(";"):
                    k, _, v = part.strip().partition("=")
                    if k == "sid":
                        return v, False
                return secrets.token_hex(16), True

            def _send(self, code, body=b"", extra=None):
                self.send_response(code)
                for k, v in (extra or {}).items():
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                sid, new = self._sid()
                with app.lock:
                    html = app.page(app.get_state(sid)).encode()
                hdr = {"Content-Type": "text/html; charset=utf-8"}
                if new:
                    hdr["Set-Cookie"] = f"sid={sid}; Path=/; HttpOnly"
                self._send(200, html, hdr)

            def do_POST(self):
                sid, new = self._sid()
                length = int(self.headers.get("Content-Length", 0))
                form = parse_qs(self.rfile.read(length).decode())
                with app.lock:
                    app.dispatch(app.get_state(sid), form.get("evt", [""])[0])
                hdr = {"Location": "/"}
                if new:
                    hdr["Set-Cookie"] = f"sid={sid}; Path=/; HttpOnly"
                self._send(303, b"", hdr)       # redirect -> refresh doesn't resubmit

            def log_message(self, *a):
                pass

        print(f"Running on http://localhost:{port}")
        ThreadingHTTPServer((host, port), Handler).serve_forever()

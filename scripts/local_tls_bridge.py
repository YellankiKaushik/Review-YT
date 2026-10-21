"""Loopback-only TLS termination for production verification, never cloud startup."""

import argparse
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()
    directory = Path(args.directory)

    class Bridge(BaseHTTPRequestHandler):
        def do_GET(self):
            self.forward()

        def do_POST(self):
            self.forward()

        def forward(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_error(400)
                return
            if length < 0:
                self.send_error(400)
                return
            if length > 4096:
                self.send_error(413)
                return
            payload = self.rfile.read(length)
            try:
                with httpx.Client(timeout=115, trust_env=False, follow_redirects=False) as client:
                    response = client.request(
                        self.command,
                        "http://127.0.0.1:5102" + self.path,
                        content=payload,
                        headers={
                            k: v
                            for k, v in self.headers.items()
                            if k.lower() in ("authorization", "content-type")
                        },
                    )
                self.send_response(response.status_code)
                self.send_header(
                    "Content-Type", response.headers.get("Content-Type", "application/json")
                )
                self.send_header("Content-Length", str(len(response.content)))
                self.end_headers()
                self.wfile.write(response.content)
            except httpx.HTTPError:
                self.send_error(503)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 5103), Bridge)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(directory / "cert.pem", directory / "key.pem")
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

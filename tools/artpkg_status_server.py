#!/usr/bin/env python3
"""Read-only ArtPkg container status service."""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.request import urlopen


STATUS_PAYLOAD = {"status": "ok", "service": "artpkg", "mode": "read-only-status"}


def json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class StatusHandler(BaseHTTPRequestHandler):
    server_version = "ArtPkgStatus/0.3.1"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._json(200, STATUS_PAYLOAD)
            return
        if self.path == "/":
            self._json(200, {**STATUS_PAYLOAD, "endpoints": ["/healthz"]})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        self._json(405, {"error": "method not allowed"})

    def do_PUT(self) -> None:
        self._json(405, {"error": "method not allowed"})

    def do_PATCH(self) -> None:
        self._json(405, {"error": "method not allowed"})

    def do_DELETE(self) -> None:
        self._json(405, {"error": "method not allowed"})

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}", file=sys.stderr)


def serve(host: str, port: int) -> int:
    server = ThreadingHTTPServer((host, port), StatusHandler)
    print(f"ArtPkg read-only status service listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


def healthcheck(host: str, port: int, timeout: float) -> int:
    url = f"http://{host}:{port}/healthz"
    with urlopen(url, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return 0 if payload == STATUS_PAYLOAD else 1


def run_questionnaire(argv: list[str]) -> int:
    import artifacts_package_questionnaire

    return artifacts_package_questionnaire.main(argv)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ArtPkg container command entrypoint.")
    sub = parser.add_subparsers(dest="command", required=True)

    serve_parser = sub.add_parser("serve", help="Run the read-only status service.")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8080)

    health_parser = sub.add_parser("healthcheck", help="Check the local read-only status endpoint.")
    health_parser.add_argument("--host", default="127.0.0.1")
    health_parser.add_argument("--port", type=int, default=8080)
    health_parser.add_argument("--timeout", type=float, default=3.0)

    questionnaire_parser = sub.add_parser("questionnaire", help="Run the ArtPkg questionnaire CLI.")
    questionnaire_parser.add_argument("questionnaire_args", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    if args.command == "serve":
        return serve(args.host, args.port)
    if args.command == "healthcheck":
        return healthcheck(args.host, args.port, args.timeout)
    if args.command == "questionnaire":
        return run_questionnaire(args.questionnaire_args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
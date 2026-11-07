"""Mara_OS development server. Standard-library only.

Set MARA_SESSION_TOKEN and OPENAI_API_KEY before use.
Bind localhost by default; use a TLS reverse proxy for remote access.
"""
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from services.dalle3 import generate_image, ImageGenerationError
from services.tasks import create_task, list_tasks

ROOT = Path(__file__).resolve().parent
MAX_BODY = 8192
TASK_DB = ROOT / "data" / "tasks.sqlite3"

class Handler(BaseHTTPRequestHandler):
    def _json(self, status, value):
        payload = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self):
        expected = os.environ.get("MARA_SESSION_TOKEN", "")
        supplied = self.headers.get("Authorization", "")
        return bool(expected) and hmac.compare_digest(supplied, "Bearer " + expected)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/tasks":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            TASK_DB.parent.mkdir(parents=True, exist_ok=True)
            return self._json(200, {"tasks": list_tasks(TASK_DB)})
        if path == "/api/health":
            return self._json(200, {"name": "Mara_OS", "status": "ok", "image_model": "dall-e-3"})
        return self._json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/images/generate", "/api/tasks"):
            return self._json(404, {"error": "Not found"})
        if not self._authorized():
            return self._json(401, {"error": "Unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                return self._json(413, {"error": "Invalid request size"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self._json(415, {"error": "Expected application/json"})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                return self._json(400, {"error": "Expected JSON object"})
            if path == "/api/tasks":
                TASK_DB.parent.mkdir(parents=True, exist_ok=True)
                ident = create_task(TASK_DB, data.get("description", ""))
                return self._json(201, {"id": ident, "state": "pending"})
            result = generate_image(
                data.get("prompt", ""), size=data.get("size", "1024x1024"),
                quality=data.get("quality", "hd"), style=data.get("style", "vivid"))
            return self._json(200, result)
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._json(400, {"error": "Invalid image request"})
        except ImageGenerationError as exc:
            self.log_error("Image generation failed: %s", type(exc).__name__)
            return self._json(502, {"error": "Image generation unavailable"})
        except Exception:
            self.log_error("Unexpected error in image generation")
            return self._json(500, {"error": "Internal server error"})

def main():
    host = os.environ.get("MARA_HOST", "127.0.0.1")
    port = int(os.environ.get("MARA_PORT", "8765"))
    if not os.environ.get("MARA_SESSION_TOKEN"):
        raise SystemExit("Set MARA_SESSION_TOKEN before starting the server")
    print(f"Mara_OS API listening on {host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    main()

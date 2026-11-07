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
from services.ai import ask_agent, analyze_image, AIError
from services.ollama_manager import status as ollama_status
from services.python_syntax import check_source
from services.global_sync import publish as sync_publish, events as sync_events
from services.vision_history import save as save_vision, list_recent as vision_history, delete_all as clear_vision_history
from services.github_read import repo_info, GitHubError
from services.openai_agents import available as agents_available, run_agent
from services.worker_registry import list_workers, add_worker, remove_worker
from services.kernel_adaptation import snapshot as kernel_snapshot
from services.resource_policy import recommend_limits
from services.live_desktop import events as desktop_events, emit as desktop_emit
from services.agent_workers import enqueue as enqueue_worker_job, get_jobs as worker_jobs
from services.desktop_planner import plan as desktop_plan
from services.kwin_bridge import native_plan as kwin_native_plan

ROOT = Path(__file__).resolve().parent
MAX_BODY = 4 * 1024 * 1024
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
        if path == "/api/sync/events":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            from urllib.parse import parse_qs
            try:
                params=parse_qs(urlsplit(self.path).query)
                return self._json(200, {"events":sync_events(params.get("since",["0"])[0])})
            except (ValueError, TypeError):
                return self._json(400, {"error":"Invalid synchronization cursor"})
        if path == "/api/vision/history":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            return self._json(200, {"items": vision_history()})
        if path == "/api/desktop/kwin-plan":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            from urllib.parse import parse_qs
            params = parse_qs(urlsplit(self.path).query)
            try:
                return self._json(200, kwin_native_plan(params.get("activity", ["idle"])[0], params.get("pinned", []), params.get("managed", [])))
            except ValueError:
                return self._json(400, {"error": "Invalid KWin plan parameters"})
        if path == "/api/desktop/layout":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            from urllib.parse import parse_qs
            params = parse_qs(urlsplit(self.path).query)
            try:
                return self._json(200, desktop_plan(params.get("activity", ["idle"])[0], params.get("pinned", [])))
            except ValueError:
                return self._json(400, {"error": "Invalid layout parameters"})
        if path == "/api/worker-jobs":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            return self._json(200, {"jobs": worker_jobs()})
        if path == "/api/desktop/events":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            from urllib.parse import parse_qs
            since = parse_qs(urlsplit(self.path).query).get("since", ["0"])[0]
            try:
                return self._json(200, {"events": desktop_events(since)})
            except ValueError:
                return self._json(400, {"error": "Invalid cursor"})
        if path == "/api/kernel/resources":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            info = kernel_snapshot()
            return self._json(200, {"kernel": info, "policy": recommend_limits(info)})
        if path == "/api/workers":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            return self._json(200, {"workers": list_workers()})
        if path == "/api/ollama/status":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            return self._json(200, ollama_status())
        if path == "/api/agents/status":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            return self._json(200, {"agents": ["Aria", "Alex", "Astyria", "Aurelius"], "sdk_available": agents_available(), "workers": False})
        if path == "/api/github/repo":
            if not self._authorized():
                return self._json(401, {"error": "Unauthorized"})
            from urllib.parse import parse_qs
            name = parse_qs(urlsplit(self.path).query).get("name", [""])[0]
            try:
                return self._json(200, repo_info(name))
            except ValueError:
                return self._json(400, {"error": "Invalid repository"})
            except GitHubError:
                return self._json(502, {"error": "GitHub unavailable"})
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
        if path not in ("/api/images/generate", "/api/tasks", "/api/ai/chat", "/api/ai/vision", "/api/agents/run", "/api/workers/create", "/api/workers/remove", "/api/desktop/events", "/api/worker-jobs", "/api/vision/history/clear", "/api/python/compile", "/api/sync/events"):
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
            if path == "/api/sync/events":
                return self._json(201, {"id":sync_publish(data.get("topic"),data.get("kind"),data.get("payload"))})
            if path == "/api/python/compile":
                return self._json(200, check_source(data.get("source")))
            if path == "/api/vision/history/clear":
                return self._json(200, {"deleted": clear_vision_history()})
            if path == "/api/worker-jobs":
                return self._json(201, {"id": enqueue_worker_job(data.get("agent"), data.get("kind"), data.get("payload"))})
            if path == "/api/desktop/events":
                return self._json(201, {"id": desktop_emit(data.get("agent"), data.get("window"), data.get("action"))})
            if path == "/api/workers/create":
                return self._json(201, {"id": add_worker(data.get("agent"), data.get("kind"))})
            if path == "/api/workers/remove":
                ident = data.get("id")
                if not isinstance(ident, str) or len(ident) != 32:
                    return self._json(400, {"error": "Invalid worker id"})
                return self._json(200, {"stopped": remove_worker(ident)})
            if path == "/api/agents/run":
                if length > 16384:
                    return self._json(413, {"error": "Agent request too large"})
                try:
                    return self._json(200, run_agent(data.get("agent", ""), data.get("message", "")))
                except RuntimeError:
                    return self._json(503, {"error": "Agents SDK unavailable or not configured"})
            if path == "/api/ai/chat":
                return self._json(200, ask_agent(data.get("agent", ""), data.get("message", "")))
            if path == "/api/ai/vision":
                result = analyze_image(data.get("question", ""), data.get("image", ""))
                if data.get("save_history") is True:
                    save_vision(data.get("agent", ""), data.get("source", "image"), data.get("question", ""), result.get("text", ""))
                return self._json(200, result)
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
        except AIError:
            return self._json(502, {"error": "AI service unavailable"})
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

"""Read-only local Ollama manager: status, installed and loaded models."""
import ipaddress
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlsplit


def _base():
    url = os.environ.get("MARA_OLLAMA_URL", "http://127.0.0.1:11434")
    parsed = urlsplit(url)
    if (parsed.scheme != "http" or parsed.username or parsed.password
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("Invalid Ollama URL")
    try:
        if not ipaddress.ip_address(parsed.hostname or "").is_loopback:
            raise ValueError("Ollama must use loopback")
    except ValueError as exc:
        raise ValueError("Invalid Ollama host") from exc
    return url.rstrip("/")


def _get(path):
    with urllib.request.urlopen(_base() + path, timeout=4) as response:
        return json.load(response)


def status():
    """No arbitrary commands or remote endpoints; never exposes API keys."""
    result = {"server": "ollama", "reachable": False, "installed_models": [],
              "loaded_models": [], "errors": [], "fallback": {
                  "provider": "Google Gemini API", "model": "gemini-3.1-flash-lite-preview",
                  "enabled": os.environ.get("MARA_GEMINI_FALLBACK", "true").lower() in ("1", "true", "yes"),
                  "configured": bool(os.environ.get("GEMINI_API_KEY")),
                  "verified": False}}
    try:
        tags = _get("/api/tags")
        result["reachable"] = True
        result["installed_models"] = [
            {"name": item.get("name"), "size": item.get("size"), "modified_at": item.get("modified_at")}
            for item in tags.get("models", []) if isinstance(item, dict)]
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        result["errors"].append("Ollama not reachable or invalid response")
        return result
    try:
        running = _get("/api/ps")
        result["loaded_models"] = [
            {"name": item.get("name"), "size": item.get("size"),
             "size_vram": item.get("size_vram"), "expires_at": item.get("expires_at")}
            for item in running.get("models", []) if isinstance(item, dict)]
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        result["errors"].append("Unable to read loaded models")
    return result

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


def _model_name(name):
    import re
    if not isinstance(name, str) or not 1 <= len(name) <= 180 or not re.fullmatch(r"[A-Za-z0-9_.:/-]+", name):
        raise ValueError("Invalid model name")
    return name


def _post(path, body, timeout=20):
    req = urllib.request.Request(_base() + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise RuntimeError("Ollama operation failed") from exc


def unload_model(name):
    """Unload a locally running model without deleting its files."""
    name = _model_name(name)
    installed = {item.get("name") for item in status()["installed_models"]}
    if name not in installed:
        raise ValueError("Model not installed")
    _post("/api/generate", {"model": name, "prompt": "", "keep_alive": 0, "stream": False})
    return {"ok": True, "action": "unload", "model": name}


def delete_model(name):
    """Delete a locally installed model, with caller-confirmed intent."""
    name = _model_name(name)
    installed = {item.get("name") for item in status()["installed_models"]}
    if name not in installed:
        raise ValueError("Model not installed")
    req = urllib.request.Request(_base() + "/api/delete", data=json.dumps({"model": name}).encode(),
                                 headers={"Content-Type": "application/json"}, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=30):
            pass
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("Unable to delete model") from exc
    return {"ok": True, "action": "delete", "model": name}

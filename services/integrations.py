"""Mara_OS optional OpenAI, Ollama, Real Vision and GitHub adapters.

All credentials stay on the server. No Gemini or deterministic response engine.
"""
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

AGENTS = ("Aria", "Alex", "Astyria", "Aurelius")
MAX_IMAGE_BYTES = 5 * 1024 * 1024

class IntegrationError(RuntimeError):
    pass

def request_json(url, *, token=None, payload=None, timeout=45):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "Mara_OS/0.1"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as exc:
        raise IntegrationError("Provider request failed") from exc

def chat(prompt, agent="Aria", provider="openai", image=None):
    if agent not in AGENTS:
        raise ValueError("Unknown agent")
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 6000:
        raise ValueError("Prompt must contain 1–6000 characters")
    if provider not in ("openai", "ollama"):
        raise ValueError("Unsupported provider")
    if image is not None:
        if provider != "openai":
            raise ValueError("Vision currently requires OpenAI")
        if not isinstance(image, dict) or image.get("mime") not in ("image/png", "image/jpeg", "image/webp"):
            raise ValueError("Unsupported image format")
        raw = base64.b64decode(image.get("base64", ""), validate=True)
        if not raw or len(raw) > MAX_IMAGE_BYTES:
            raise ValueError("Image must be 1 byte to 5 MB")
    instruction = f"You are {agent}, one of four equal Mara_OS AI agents. Reply in Polish unless requested otherwise. Do not claim to have executed system actions."
    if provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise IntegrationError("OpenAI is not configured")
        model = os.environ.get("MARA_OPENAI_MODEL", "gpt-4o-mini")
        content = [{"type": "text", "text": prompt.strip()}]
        if image:
            content.append({"type": "image_url", "image_url": {"url": f"data:{image['mime']};base64,{image['base64']}"}})
        data = request_json("https://api.openai.com/v1/chat/completions", token=key, payload={
            "model": model, "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": content}],
            "max_tokens": 800
        }, timeout=90)
        return {"agent": agent, "provider": "openai", "text": data["choices"][0]["message"]["content"]}
    # Local Ollama only; never allow user-provided arbitrary endpoint URLs.
    host = os.environ.get("MARA_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    if host not in ("http://127.0.0.1:11434", "http://localhost:11434"):
        raise IntegrationError("Only local Ollama endpoint is permitted")
    data = request_json(host + "/api/chat", payload={
        "model": os.environ.get("MARA_OLLAMA_MODEL", "qwen3:14b"),
        "stream": False, "messages": [{"role": "system", "content": instruction},
                                       {"role": "user", "content": prompt.strip()}]
    }, timeout=90)
    return {"agent": agent, "provider": "ollama", "text": data["message"]["content"]}

def github_repo_status(owner, name):
    """Read repository metadata using optional server-side GitHub token."""
    import re
    if not all(isinstance(v, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", v) for v in (owner, name)):
        raise ValueError("Invalid GitHub repository")
    url = "https://api.github.com/repos/" + urllib.parse.quote(owner) + "/" + urllib.parse.quote(name)
    data = request_json(url, token=os.environ.get("GITHUB_TOKEN"))
    return {"full_name": data.get("full_name"), "default_branch": data.get("default_branch"),
            "open_issues": data.get("open_issues_count"), "html_url": data.get("html_url")}

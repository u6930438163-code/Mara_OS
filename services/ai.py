"""Mara_OS OpenAI text and Real Vision adapter; server-side credentials only."""
import base64
import ipaddress
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlsplit

class AIError(RuntimeError):
    pass

AGENTS = ("Aria", "Alex", "Astyria", "Aurelius")
API = "https://api.openai.com/v1/chat/completions"

def _request(messages, *, vision=False):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise AIError("OPENAI_API_KEY is not configured")
    model = os.environ.get("MARA_VISION_MODEL" if vision else "MARA_TEXT_MODEL", "gpt-4o-mini")
    payload = json.dumps({"model": model, "messages": messages, "max_tokens": 800}).encode()
    req = urllib.request.Request(API, data=payload, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.load(res)
        return {"model": model, "text": data["choices"][0]["message"]["content"]}
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, IndexError, ValueError) as exc:
        raise AIError("AI provider request failed") from exc


def _ollama(messages, *, vision=False):
    """Local Ollama adapter; never forward images to a third-party endpoint."""
    base = os.environ.get("MARA_OLLAMA_URL", "http://127.0.0.1:11434")
    try:
        parsed = urlsplit(base)
    except ValueError as exc:
        raise AIError("Invalid Ollama endpoint") from exc
    # Prevent this service from becoming an SSRF proxy.
    if parsed.scheme != "http" or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise AIError("Invalid Ollama endpoint")
    try:
        if not ipaddress.ip_address(parsed.hostname).is_loopback:
            raise AIError("Ollama must be bound to loopback")
    except (ValueError, TypeError) as exc:
        raise AIError("Ollama endpoint must be a loopback IP") from exc
    model = os.environ.get("MARA_OLLAMA_VISION_MODEL" if vision else "MARA_OLLAMA_TEXT_MODEL",
                           "llama3.2-vision:11b" if vision else "hf.co/mradermacher/Floppa-12B-Gemma3-Uncensored-GGUF:Q8_0")
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/api/chat", data=payload, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.load(response)
        return {"model": model, "text": data["message"]["content"], "provider": "ollama"}
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TypeError, ValueError) as exc:
        raise AIError("Ollama request failed") from exc

def ask_agent(agent, message):
    if agent not in AGENTS or not isinstance(message, str) or not 1 <= len(message.strip()) <= 8000:
        raise ValueError("Invalid agent or message")
    provider = os.environ.get("MARA_TEXT_PROVIDER", "openai").lower()
    if provider not in ("openai", "ollama"):
        raise AIError("Unsupported text provider")
    request = _ollama if provider == "ollama" else _request
    return request([
        {"role": "system", "content": f"You are {agent}, a Mara_OS collaborator. Answer in Polish. Do not claim you executed tools or changed the OS unless confirmed."},
        {"role": "user", "content": message.strip()}
    ])

def analyze_image(question, image_data_url):
    """Accept only bounded JPEG/PNG/WEBP base64 data URLs; no arbitrary remote fetch."""
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 4000:
        raise ValueError("Invalid question")
    if not isinstance(image_data_url, str) or len(image_data_url) > 5_000_000:
        raise ValueError("Invalid image")
    prefixes = ("data:image/jpeg;base64,", "data:image/png;base64,", "data:image/webp;base64,")
    if not image_data_url.startswith(prefixes):
        raise ValueError("Only base64 JPEG, PNG and WEBP images are supported")
    provider = os.environ.get("MARA_VISION_PROVIDER", "ollama").lower()
    if provider not in ("openai", "ollama"):
        raise AIError("Unsupported vision provider")
    if provider == "ollama":
        encoded = image_data_url.split(",", 1)[1]
        try:
            base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ValueError("Invalid base64 image") from exc
        return _ollama([
            {"role": "system", "content": "You are Mara_OS Real Vision. Analyze accurately in Polish. Separate observations from inferences."},
            {"role": "user", "content": question.strip(), "images": [encoded]}
        ], vision=True)
    return _request([
        {"role": "system", "content": "You are Mara_OS Real Vision. Analyze the supplied image accurately, in Polish. Distinguish observations from inferences."},
        {"role": "user", "content": [{"type": "text", "text": question.strip()}, {"type": "image_url", "image_url": {"url": image_data_url, "detail": "auto"}}]}
    ], vision=True)

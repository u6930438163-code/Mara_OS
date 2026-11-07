"""Mara_OS AI adapters: local Ollama, optional Gemini fallback, and OpenAI."""
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
    payload = json.dumps({"model": model, "messages": messages, "max_tokens": int(os.environ.get("MARA_MAX_OUTPUT_TOKENS", "8192"))}).encode()
    req = urllib.request.Request(API, data=payload, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.load(res)
        return {"model": model, "text": data["choices"][0]["message"]["content"], "provider": "openai", "provider_name": "OpenAI API", "fallback": False, "source": "api"}
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, IndexError, ValueError) as exc:
        raise AIError("AI provider request failed") from exc

def _ollama(messages, *, vision=False):
    base = os.environ.get("MARA_OLLAMA_URL", "http://127.0.0.1:11434")
    try:
        parsed = urlsplit(base)
        if parsed.scheme != "http" or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise AIError("Invalid Ollama endpoint")
        if not ipaddress.ip_address(parsed.hostname).is_loopback:
            raise AIError("Ollama must be bound to loopback")
    except (ValueError, TypeError) as exc:
        raise AIError("Invalid Ollama endpoint") from exc
    model = os.environ.get("MARA_OLLAMA_VISION_MODEL" if vision else "MARA_OLLAMA_TEXT_MODEL",
                           "llama3.2-vision:11b" if vision else "hf.co/mradermacher/Floppa-12B-Gemma3-Uncensored-GGUF:Q8_0")
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/api/chat", data=payload, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.load(response)
        return {"model": model, "text": data["message"]["content"], "provider": "ollama", "provider_name": "Ollama (local)", "fallback": False, "source": "local"}
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TypeError, ValueError, TimeoutError) as exc:
        raise AIError("Ollama request failed") from exc

def _gemini(messages, *, vision=False):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise AIError("Gemini fallback unavailable: GEMINI_API_KEY missing")
    model = "gemini-3.1-flash-lite-preview"
    parts = []
    for message in messages:
        content = message.get("content", "")
        if message.get("role") == "system":
            parts.append({"text": str(content)})
        elif message.get("images"):
            parts.append({"text": str(content)})
            for encoded in message["images"]:
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded}})
        else:
            parts.append({"text": str(content)})
    payload = json.dumps({"contents": [{"role": "user", "parts": parts}],
                          "generationConfig": {"maxOutputTokens": int(os.environ.get("MARA_MAX_OUTPUT_TOKENS", "8192"))}}).encode()
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent"
    req = urllib.request.Request(url, data=payload, method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.load(response)
        text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
        if not text:
            raise AIError("Gemini returned no text")
        return {"model": model, "text": text, "provider": "gemini", "provider_name": "Google Gemini API", "fallback": True, "source": "api", "fallback_from": "ollama"}
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, IndexError, TypeError, ValueError, TimeoutError) as exc:
        raise AIError("Gemini fallback request failed") from exc

def _with_fallback(messages, *, vision=False, provider="ollama"):
    if provider == "openai":
        return _request(messages, vision=vision)
    try:
        return _ollama(messages, vision=vision)
    except AIError:
        if os.environ.get("MARA_GEMINI_FALLBACK", "true").lower() not in ("1", "true", "yes"):
            raise
        return _gemini(messages, vision=vision)

def ask_agent(agent, message):
    if agent not in AGENTS or not isinstance(message, str) or not 1 <= len(message.strip()) <= 100000:
        raise ValueError("Invalid agent or message")
    provider = os.environ.get("MARA_TEXT_PROVIDER", "ollama").lower()
    if provider not in ("openai", "ollama"):
        raise AIError("Unsupported text provider")
    return _with_fallback([
        {"role": "system", "content": f"You are {agent}, a Mara_OS collaborator. Answer in Polish. Do not claim you executed tools or changed the OS unless confirmed."},
        {"role": "user", "content": message.strip()}
    ], provider=provider)

def analyze_image(question, image_data_url):
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 4000:
        raise ValueError("Invalid question")
    if not isinstance(image_data_url, str) or len(image_data_url) > 5_000_000:
        raise ValueError("Invalid image")
    prefixes = {"image/jpeg": "data:image/jpeg;base64,", "image/png": "data:image/png;base64,", "image/webp": "data:image/webp;base64,"}
    mime = next((m for m, prefix in prefixes.items() if image_data_url.startswith(prefix)), None)
    if not mime:
        raise ValueError("Only base64 JPEG, PNG and WEBP images are supported")
    encoded = image_data_url.split(",", 1)[1]
    try:
        base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError("Invalid base64 image") from exc
    provider = os.environ.get("MARA_VISION_PROVIDER", "ollama").lower()
    if provider not in ("openai", "ollama"):
        raise AIError("Unsupported vision provider")
    if provider == "openai":
        return _request([
            {"role": "system", "content": "You are Mara_OS Real Vision. Analyze accurately in Polish."},
            {"role": "user", "content": [{"type": "text", "text": question.strip()}, {"type": "image_url", "image_url": {"url": image_data_url, "detail": "auto"}}]}
        ], vision=True)
    try:
        return _ollama([
            {"role": "system", "content": "You are Mara_OS Real Vision. Analyze accurately in Polish. Separate observations from inferences."},
            {"role": "user", "content": question.strip(), "images": [encoded]}
        ], vision=True)
    except AIError:
        if os.environ.get("MARA_GEMINI_FALLBACK", "true").lower() not in ("1", "true", "yes"):
            raise
        return _gemini([
            {"role": "system", "content": "Analyze accurately in Polish. Separate observations from inferences."},
            {"role": "user", "content": question.strip(), "images": [encoded]}
        ], vision=True)

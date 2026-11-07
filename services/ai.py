"""Mara_OS OpenAI text and Real Vision adapter; server-side credentials only."""
import json
import os
import urllib.error
import urllib.request

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

def ask_agent(agent, message):
    if agent not in AGENTS or not isinstance(message, str) or not 1 <= len(message.strip()) <= 8000:
        raise ValueError("Invalid agent or message")
    return _request([
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
    return _request([
        {"role": "system", "content": "You are Mara_OS Real Vision. Analyze the supplied image accurately, in Polish. Distinguish observations from inferences."},
        {"role": "user", "content": [{"type": "text", "text": question.strip()}, {"type": "image_url", "image_url": {"url": image_data_url, "detail": "auto"}}]}
    ], vision=True)

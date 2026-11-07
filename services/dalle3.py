"""Server-side DALL-E 3 image generation for Mara_OS.

Requires OPENAI_API_KEY in the server environment.
No API key is ever sent to the browser.
"""
import json
import os
import urllib.error
import urllib.request

OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
ALLOWED_SIZES = {"1024x1024", "1024x1792", "1792x1024"}
ALLOWED_QUALITIES = {"standard", "hd"}
ALLOWED_STYLES = {"vivid", "natural"}

class ImageGenerationError(RuntimeError):
    pass

def generate_image(prompt: str, *, size: str = "1024x1024",
                   quality: str = "hd", style: str = "vivid") -> dict:
    """Return a DALL-E 3 result with a temporary image URL.

    Call only from an authenticated backend route with quotas and rate limiting.
    """
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 4000:
        raise ValueError("Prompt must contain 1–4000 characters")
    if size not in ALLOWED_SIZES or quality not in ALLOWED_QUALITIES or style not in ALLOWED_STYLES:
        raise ValueError("Unsupported DALL-E 3 settings")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ImageGenerationError("OPENAI_API_KEY is not configured")
    payload = json.dumps({
        "model": "dall-e-3", "prompt": prompt.strip(), "n": 1,
        "size": size, "quality": quality, "style": style,
        "response_format": "url"
    }).encode("utf-8")
    req = urllib.request.Request(
        OPENAI_IMAGES_URL, data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not expose provider response bodies, which may contain sensitive data.
        raise ImageGenerationError(f"OpenAI image request failed (HTTP {exc.code})") from exc
    except urllib.error.URLError as exc:
        raise ImageGenerationError("OpenAI image service unavailable") from exc
    images = result.get("data", [])
    if not images or not images[0].get("url"):
        raise ImageGenerationError("OpenAI did not return an image URL")
    return {"model": "dall-e-3", "url": images[0]["url"],
            "revised_prompt": images[0].get("revised_prompt")}

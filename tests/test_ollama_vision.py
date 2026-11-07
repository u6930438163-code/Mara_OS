"""Offline regression tests for Mara_OS Ollama Vision adapter.

Run: python3 -m unittest discover -s tests -p 'test_ollama_vision.py'
"""
import base64
import json
import os
import unittest
from unittest.mock import patch
from services.ai import AIError, analyze_image, ask_agent


class FakeResponse:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, *args):
        return json.dumps({"message": {"content": "Widzę pulpit."}}).encode()


class OllamaVisionTests(unittest.TestCase):
    def setUp(self):
        self.image = "data:image/png;base64," + base64.b64encode(b"image-bytes").decode()

    def test_vision_uses_local_ollama_and_image_payload(self):
        captured = {}
        def fake_open(request, timeout):
            captured["url"] = request.full_url
            captured["payload"] = json.loads(request.data)
            return FakeResponse()
        with patch.dict(os.environ, {"MARA_VISION_PROVIDER": "ollama", "MARA_OLLAMA_URL": "http://127.0.0.1:11434"}):
            with patch("services.ai.urllib.request.urlopen", side_effect=fake_open):
                result = analyze_image("Co widać?", self.image)
        self.assertEqual(captured["url"], "http://127.0.0.1:11434/api/chat")
        self.assertEqual(captured["payload"]["messages"][-1]["images"], [self.image.split(",",1)[1]])
        self.assertEqual(result["provider"], "ollama")

    def test_invalid_base64_rejected(self):
        with patch.dict(os.environ, {"MARA_VISION_PROVIDER": "ollama"}):
            with self.assertRaises(ValueError):
                analyze_image("Co widać?", "data:image/png;base64,not!base64")

    def test_nonlocal_endpoint_rejected(self):
        with patch.dict(os.environ, {"MARA_VISION_PROVIDER": "ollama", "MARA_OLLAMA_URL": "http://example.com:11434"}):
            with self.assertRaises(AIError):
                analyze_image("Co widać?", self.image)

    def test_text_provider_can_use_ollama(self):
        with patch.dict(os.environ, {"MARA_TEXT_PROVIDER": "ollama", "MARA_OLLAMA_URL": "http://127.0.0.1:11434"}):
            with patch("services.ai.urllib.request.urlopen", return_value=FakeResponse()):
                result = ask_agent("Aria", "Cześć")
        self.assertEqual(result["provider"], "ollama")


if __name__ == "__main__":
    unittest.main()

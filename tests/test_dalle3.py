import os
import unittest
from unittest.mock import patch
from services.dalle3 import generate_image, ImageGenerationError

class Dalle3Tests(unittest.TestCase):
    def test_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            generate_image(" ")

    def test_rejects_unsupported_size(self):
        with self.assertRaises(ValueError):
            generate_image("A violet moon", size="512x512")

    def test_rejects_oversized_prompt(self):
        with self.assertRaises(ValueError):
            generate_image("x" * 4001)

    def test_missing_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaises(ImageGenerationError):
                generate_image("A violet moon")

if __name__ == "__main__":
    unittest.main()

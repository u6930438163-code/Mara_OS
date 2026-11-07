import unittest
from services.ai import ask_agent, analyze_image
from services.github_read import repo_info

class IntegrationTests(unittest.TestCase):
    def test_invalid_agent(self):
        with self.assertRaises(ValueError):
            ask_agent("Unknown", "Hello")
    def test_invalid_image(self):
        with self.assertRaises(ValueError):
            analyze_image("What is this?", "https://example.com/test.png")
    def test_invalid_repo(self):
        with self.assertRaises(ValueError):
            repo_info("https://github.com/example/repo")
if __name__ == "__main__":
    unittest.main()

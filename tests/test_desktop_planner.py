"""Unit tests for Mara_OS live desktop layout planning."""
import unittest
from services.desktop_planner import plan

class DesktopPlannerTests(unittest.TestCase):
    def test_diagnostics(self):
        result = plan("diagnostics")
        self.assertEqual(result["visible"], ["terminal", "logs", "resources"])
        self.assertIn("chat", result["hidden"])
    def test_pinned_preserved(self):
        result = plan("idle", pinned=["terminal"])
        self.assertEqual(result["visible"], ["terminal", "chat"])
        self.assertNotIn("terminal", result["hidden"])
    def test_invalid_activity(self):
        with self.assertRaises(ValueError):
            plan("destroy")
    def test_invalid_pin(self):
        with self.assertRaises(ValueError):
            plan("chat", pinned=["unknown"])
    def test_no_duplicates(self):
        result = plan("chat", pinned=["chat"])
        self.assertEqual(result["visible"].count("chat"), 1)

if __name__ == "__main__":
    unittest.main()

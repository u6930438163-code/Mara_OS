"""Tests for KWin native layout adapter (no KDE session required)."""
import unittest
from services.kwin_bridge import native_plan

class KWinBridgeTests(unittest.TestCase):
    def test_managed_windows_only(self):
        result = native_plan("diagnostics", managed_app_ids=["org.kde.konsole", "org.kde.dolphin", "org.other.App"])
        self.assertEqual(result["show_app_ids"], ["org.kde.konsole"])
        self.assertEqual(result["minimize_app_ids"], ["org.kde.dolphin"])
        self.assertFalse(result["applied"])
    def test_pinned_file_manager(self):
        result = native_plan("diagnostics", pinned=["files"], managed_app_ids=["org.kde.dolphin"])
        self.assertIn("org.kde.dolphin", result["show_app_ids"])
        self.assertNotIn("org.kde.dolphin", result["minimize_app_ids"])
    def test_unknown_activity(self):
        with self.assertRaises(ValueError):
            native_plan("invalid")
if __name__ == "__main__":
    unittest.main()

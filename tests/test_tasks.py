import tempfile
import unittest
from pathlib import Path
from services.tasks import create_task, list_tasks, claim_task, finish_task

class TaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "tasks.db"
    def tearDown(self):
        self.tmp.cleanup()
    def test_claim_once(self):
        ident = create_task(self.db, "Check logs")
        self.assertEqual(claim_task(self.db, "Aria"), ident)
        self.assertIsNone(claim_task(self.db, "Alex"))
        self.assertFalse(finish_task(self.db, ident, "Alex"))
        self.assertTrue(finish_task(self.db, ident, "Aria"))
        self.assertEqual(list_tasks(self.db)[0]["state"], "done")
    def test_validation(self):
        with self.assertRaises(ValueError):
            create_task(self.db, " ")
        with self.assertRaises(ValueError):
            claim_task(self.db, "Unknown")
if __name__ == "__main__":
    unittest.main()

"""Checks that Real Vision workers can be created and claimed."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services import agent_workers, worker_registry

class VisionRegistryTests(unittest.TestCase):
    def test_vision_worker_slot_and_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(agent_workers, "DB_PATH", Path(tmp) / "workers.sqlite3"):
                slot = worker_registry.add_worker("Aria", "vision_report")
                workers = worker_registry.list_workers()
                self.assertTrue(any(w["id"] == slot and w["kind"] == "vision_report" for w in workers))
                job = agent_workers.enqueue("Aria", "vision_report", "Opis pulpitu")
                claimed = agent_workers.claim("Aria", "vision_report")
                self.assertEqual(claimed["id"], job)
                self.assertTrue(worker_registry.remove_worker(slot))

    def test_reject_invalid_worker_kind(self):
        with self.assertRaises(ValueError):
            worker_registry.add_worker("Aria", "shell")

if __name__ == "__main__":
    unittest.main()

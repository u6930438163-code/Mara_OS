"""Regression checks for Vision-to-worker routing, without an AI provider."""
import asyncio
import os
import tempfile
import unittest
from unittest.mock import patch

from services import agent_workers


class VisionWorkerTests(unittest.TestCase):
    def test_vision_report_is_queued_without_image(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(agent_workers, "DB_PATH", __import__("pathlib").Path(directory)/"workers.db"):
                ident=agent_workers.enqueue("Aria","vision_report","Raport: na ekranie jest okno.")
                jobs=agent_workers.get_jobs()
                self.assertEqual(jobs[0]["id"],ident)
                self.assertEqual(jobs[0]["state"],"pending")
                claimed=agent_workers.claim("Aria","vision_report")
                self.assertEqual(claimed["payload"],"Raport: na ekranie jest okno.")

    def test_reject_unknown_agent(self):
        with self.assertRaises(ValueError):
            agent_workers.enqueue("Nieznany","vision_report","Raport")

    def test_worker_calls_agent_text_adapter(self):
        async def run():
            with patch("services.ai.ask_agent",return_value={"text":"Proponuję sprawdzić logi."}) as mock:
                result=await agent_workers.execute("Alex",{"kind":"vision_report","payload":"Opis obrazu"})
                self.assertEqual(result,"Proponuję sprawdzić logi.")
                mock.assert_called_once_with("Alex","Opis obrazu")
        asyncio.run(run())


if __name__=="__main__":
    unittest.main()

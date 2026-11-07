import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from services import global_sync

class GlobalSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.patch=patch.object(global_sync,"DB_PATH",Path(self.tmp.name)/"sync.sqlite3")
        self.patch.start()
    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()
    def test_ordered_replay(self):
        a=global_sync.publish("chat","message",{"text":"pierwsza"})
        b=global_sync.publish("workers","changed",{"worker":"Aria"})
        self.assertLess(a,b)
        self.assertEqual([e["id"] for e in global_sync.events()],[a,b])
        self.assertEqual([e["id"] for e in global_sync.events(since=a)],[b])
    def test_validation(self):
        with self.assertRaises(ValueError):
            global_sync.publish("unknown","message",{})
        with self.assertRaises(ValueError):
            global_sync.publish("chat","message",{"text":"x"*20000})
        with self.assertRaises(ValueError):
            global_sync.events(since=-1)
    def test_payload(self):
        global_sync.publish("vision","updated",{"name":"Żółw"})
        self.assertEqual(global_sync.events()[0]["payload"]["name"],"Żółw")

if __name__=="__main__":
    unittest.main()

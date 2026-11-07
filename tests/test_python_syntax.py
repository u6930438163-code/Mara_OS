"""Syntax compiler regression tests; no user code is executed."""
import unittest
from services.python_syntax import check_source

class PythonSyntaxTests(unittest.TestCase):
    def test_valid_source(self):
        self.assertEqual(check_source("print('ok')")["state"], "compiled")
    def test_syntax_error(self):
        result=check_source("def bad(\n")
        self.assertFalse(result["ok"])
        self.assertEqual(result["state"],"syntax_error")
    def test_no_execution(self):
        result=check_source("raise RuntimeError('must not run')")
        self.assertTrue(result["ok"])
    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            check_source("")

if __name__=="__main__":
    unittest.main()

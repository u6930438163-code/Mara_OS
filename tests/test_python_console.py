"""Local Python console tests. No privileged operations are performed."""
import tempfile
import unittest
from pathlib import Path
from shell.python_console import execute

class PythonConsoleTests(unittest.TestCase):
    def test_compile_and_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"demo.py"
            source.write_text("print('Mara Python OK')\n", encoding="utf-8")
            self.assertEqual(execute(source,compile_only=True)["state"],"compiled")
            result=execute(source)
            self.assertEqual(result["state"],"done")
            self.assertIn("Mara Python OK",result["stdout"])

    def test_syntax_error(self):
        import py_compile
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"invalid.py"
            source.write_text("def broken(\n",encoding="utf-8")
            with self.assertRaises(py_compile.PyCompileError):
                execute(source)

    def test_reject_non_python_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"script.sh"
            source.write_text("echo hi",encoding="utf-8")
            with self.assertRaises(ValueError):
                execute(source)

if __name__=="__main__":
    unittest.main()

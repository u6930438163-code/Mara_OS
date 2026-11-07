#!/usr/bin/env python3
"""Mara Python Console: local-only Python compiler and shell-capable runner.

Runs Python with the privileges of the invoking OS account. For administrator
execution, an operator must explicitly start this CLI using sudo. No HTTP API.
"""
import argparse
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import time

MAX_SOURCE_BYTES = 256_000
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 120
MAX_OUTPUT_BYTES = 64_000


def execute(path, *, timeout=DEFAULT_TIMEOUT, compile_only=False):
    source = Path(path).resolve(strict=True)
    if not source.is_file() or source.suffix != ".py":
        raise ValueError("Provide an existing .py file")
    if not 1 <= source.stat().st_size <= MAX_SOURCE_BYTES:
        raise ValueError("Python source exceeds size limit or is empty")
    if not 1 <= timeout <= MAX_TIMEOUT:
        raise ValueError("Timeout must be 1..120 seconds")
    with tempfile.TemporaryDirectory(prefix="mara-py-") as tmp:
        py_compile.compile(str(source), cfile=str(Path(tmp) / "program.pyc"), doraise=True)
        if compile_only:
            return {"state": "compiled", "file": str(source)}
        # No shell=True. Python code itself can invoke the system shell:
        # this is a privileged developer tool, not a sandbox.
        started = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, "-B", str(source)], stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=timeout, cwd=str(source.parent), check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {"state": "timeout", "elapsed": round(time.monotonic()-started, 2),
                    "stdout": (exc.stdout or b"")[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
                    "stderr": (exc.stderr or b"")[:MAX_OUTPUT_BYTES].decode("utf-8", "replace")}
        return {"state": "done" if proc.returncode == 0 else "failed",
                "exit_code": proc.returncode,
                "euid": os.geteuid() if hasattr(os, "geteuid") else None,
                "elapsed": round(time.monotonic()-started, 2),
                "stdout": proc.stdout[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
                "stderr": proc.stderr[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
                "truncated": len(proc.stdout)>MAX_OUTPUT_BYTES or len(proc.stderr)>MAX_OUTPUT_BYTES}


def main():
    import json
    parser = argparse.ArgumentParser(description="Mara_OS local Python compiler / runner")
    parser.add_argument("file", help="Existing Python .py source file")
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    try:
        print(json.dumps(execute(args.file, timeout=args.timeout, compile_only=args.compile_only),
                         ensure_ascii=False, indent=2))
    except (ValueError, OSError, py_compile.PyCompileError) as exc:
        parser.exit(2, f"Python Console error: {exc}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Mara Shell: safe async Linux shell orchestration prototype.

No arbitrary shell execution: only explicit read-only command adapters.
"""
import argparse
import asyncio
import json
import shutil
import sys
import time

COMMANDS = {
    "system": ("uname", "-a"),
    "memory": ("free", "-h"),
    "disk": ("df", "-h"),
    "processes": ("ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"),
    "services": ("systemctl", "--failed", "--no-pager"),
}
TIMEOUT = 12
OUTPUT_LIMIT = 24000

async def run_adapter(name):
    if name not in COMMANDS:
        raise ValueError("Unknown adapter")
    argv = COMMANDS[name]
    if shutil.which(argv[0]) is None:
        return {"adapter": name, "state": "unavailable", "reason": "Command not installed"}
    started = time.monotonic()
    process = await asyncio.create_subprocess_exec(*argv, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(process.communicate(), timeout=TIMEOUT)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        return {"adapter": name, "state": "timeout", "elapsed": round(time.monotonic()-started, 3)}
    return {"adapter": name, "state": "done" if process.returncode == 0 else "failed",
            "exit_code": process.returncode, "elapsed": round(time.monotonic()-started, 3),
            "stdout": out[:OUTPUT_LIMIT].decode("utf-8", "replace"),
            "stderr": err[:OUTPUT_LIMIT].decode("utf-8", "replace"),
            "truncated": len(out)>OUTPUT_LIMIT or len(err)>OUTPUT_LIMIT}

async def main():
    parser = argparse.ArgumentParser(description="Mara Shell: asynchronous Linux diagnostics")
    parser.add_argument("adapters", nargs="*", choices=tuple(COMMANDS))
    args = parser.parse_args()
    names = args.adapters or ["system", "memory", "disk"]
    results = await asyncio.gather(*(run_adapter(n) for n in names))
    print(json.dumps({"shell": "Mara Shell", "results": results}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)

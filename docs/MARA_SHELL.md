# Mara Shell — polymorphic, asynchronous, asymmetric Linux shell

Mara Shell is a **user-space shell/orchestrator**, not the Linux kernel and not a replacement for KDE Plasma. The first implementation is a Python CLI with multiple command adapters, asynchronous subprocess execution and bounded diagnostic output.

## Implemented
- `shell/mara_shell.py` — dispatches named adapters through a shared `run_adapter` interface (polymorphic adapter dispatch).
- Concurrent execution with `asyncio.gather`; each command has a timeout.
- Distinct execution profiles can be added per adapter (asymmetry); the initial prototype uses a shared timeout and output limit.
- Fixed read-only diagnostic commands: system, memory, disk, processes, services.
- JSON output with exit code, elapsed time, stdout, stderr and truncation flags.

## Run on Debian/Linux
```bash
python3 shell/mara_shell.py system memory disk
python3 shell/mara_shell.py processes services
```

No root access is required for basic diagnostics. Commands may fail or be unavailable depending on the Linux environment. Do not pass untrusted command strings to subprocesses.

## Next stages
Integrate with the async core, persistent jobs, four agents' audit logs and the Mara_OS UI. Implement adapter-specific resource budgets and safe cancellation. KDE integration requires native KDE running on Linux.

**This is an initial prototype, not a replacement login shell or installed system service.**

# Mara_OS: autonomous asynchronous agents and root access

Linux Kernel is the **only kernel**. Mara Shell, workers and AI models run in user space.

## Implemented
- `services/agent_workers.py`: four independent asynchronous worker loops for Aria, Alex, Astyria and Aurelius.
- SQLite WAL durable job queue with pending/running/done/failed states and per-job event history.
- Background chat tasks via optional OpenAI Agents SDK, and fixed read-only Linux diagnostic adapters.
- Worker restart recovery: running jobs are requeued. This is at-least-once processing; tasks with side effects need idempotency before enabling them.
- `deploy/mara-agent-workers.service`: hardened systemd service, runs as a dedicated unprivileged `mara-agents` user, automatically restarts.

## Root policy
Agents must **not** run unrestricted model-generated shell commands as root. The worker service deliberately drops Linux capabilities. For administrator actions, add a separate narrowly-scoped privileged broker with allowlisted operations, explicit operator approval for changes, authentication, audit and policy enforcement. No root broker has been implemented in this commit.

## Run on a compatible Debian Linux host
1. Install the repo in `/opt/mara-os` and create dedicated user/group `mara-agents`.
2. Install dependencies into `/opt/mara-os/.venv-ai` using `scripts/install-openai-linux.sh`.
3. Create `/opt/mara-os/data` owned by `mara-agents`.
4. Set server-only `OPENAI_API_KEY` in a restricted `/etc/mara-os/agents.env` (permissions 0600); never commit credentials.
5. Review service file, then install to `/etc/systemd/system/mara-agent-workers.service`, `systemctl daemon-reload`, `systemctl enable --now mara-agent-workers.service`.
6. Check `journalctl -u mara-agent-workers.service -f`.

## Not yet implemented
- API endpoints for enqueue/status/events, frontend live subscriptions, permissions broker, workload-specific concurrency profiles, production deployment tests.
- This worker service has not been installed or started on a real host.

# Mara_OS — AI diagnostics catalog (proposed)

Target: four agents (Aria, Alex, Astyria, Aurelius), mobile-first UI, native KDE Plasma 6.8.2 target. This catalog is **not an installation record**.

| Area | Tools / interfaces |
|---|---|
| Linux | btop, systemd-analyze, journalctl, lsof, strace |
| KDE Plasma | KWin support information, qdbus6, kscreen-doctor, coredumpctl, Qt logging |
| Android hardware | Termux:API, adb, dumpsys, Perfetto, smartctl (where supported) |
| Networking | mtr, tcpdump, tshark, iperf3, dig |
| Security | Lynis, ClamAV, AIDE, auditd, OpenSCAP |
| Containers/processes | Podman, cgroups, nsenter, psutil, systemctl |
| AI observability | OpenAI health checks, optional Ollama diagnostics, Prometheus, OpenTelemetry, Langfuse |
| GitHub | gh, GitHub Actions, Semgrep, Trivy, Gitleaks |
| APIs/tests | curl, HTTPie, pytest, Playwright, k6 |
| Storage | ncdu, duf, SQLite integrity_check, restic, rclone check |

## Permission model
- Default to read-only inspection and redact credentials, tokens, prompts, private files and personally identifying data from diagnostics.
- Privileged operations, packet capture, process tracing and agent repairs require explicit authorization and scoped execution.
- Diagnostics must report source, timestamp, agent identity, exit code and stderr; distinguish simulated data from live measurements.
- Each agent has its own session and sandbox, with a common UI; no unrestricted root or access to another agent's secrets.
- AI Studio frontend should call an authenticated diagnostics backend. It cannot run native KDE or Linux utilities by itself.

## First implementation milestones
1. Read-only health endpoints for API, task queue, GitHub integration and agent connectivity.
2. Structured logs: success/error, filters, correlation IDs and per-agent activity.
3. Mobile diagnostics dashboard with explicit availability states (unavailable / configured / healthy / error).
4. Opt-in runner with command allowlist, timeouts, output caps and audit logs on a real Linux host.
5. Validate native KDE and Android hardware compatibility before enabling KDE/ADB tools.

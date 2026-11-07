# AILinux integration plan for Mara_OS

Upstream author: https://github.com/derleiti
Potential upstream components (verify existence, current licensing and compatibility before use):
- https://github.com/derleiti/ailinux-app
- https://github.com/derleiti/ai-coder
- https://github.com/derleiti/triforce-dev-mcp
- https://github.com/derleiti/ailinux-helper
- https://github.com/derleiti/build_linux

## Status
Planning only. No upstream source code, packages, services or images have been imported or installed. Do not imply AILinux is running.

## Integration requirements
1. Verify upstream project and license for each component; do not redistribute proprietary or unclear-license code.
2. Identify the actual distro base, boot image/build instructions and dependencies. Preserve Mara_OS as an independent system.
3. Implement an adapter for Mara_OS agent identities Aria, Astyria, Alex and Aurelius with explicit per-agent credentials and audit trails.
4. Expose optional MCP integration through authenticated endpoints; never hardcode API keys.
5. Require explicit approval before privileged operations. Use least privilege by default and a separately authorized root execution broker for necessary system administration.
6. Add CI build checks, license inventory, sandboxed tests, rollback and upgrade path before enabling integrations.
7. Preserve existing Mara_OS main functionality and agent routing.

This document records requested integration work; it is not a completed installation.

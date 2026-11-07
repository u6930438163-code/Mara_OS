# Mara_OS — OpenAI integrations for Debian/Linux

## Implemented in repository
- Existing server-side OpenAI text chat and image analysis: `services/ai.py` with authenticated `/api/ai/chat` and `/api/ai/vision`.
- Optional tool-free OpenAI Agents SDK adapter: `services/openai_agents.py`; one of Aria/Alex/Astyria/Aurelius, each with a distinct agent name. Not a background worker.
- Optional Python dependencies: `requirements-ai.txt`.
- Local virtual environment installer: `bash scripts/install-openai-linux.sh`. It does **not** run automatically or require sudo.

## To enable on a Linux host
1. Review `scripts/install-openai-linux.sh` and dependencies.
2. Run `bash scripts/install-openai-linux.sh` in the repository directory.
3. Supply `OPENAI_API_KEY` as a secret on the **server**, never in frontend code or Git.
4. Configure `MARA_SESSION_TOKEN` for the existing API. Test existing chat/vision routes.
5. Codex CLI is **optional**, separately installed after reviewing its permissions: `npm install -g @openai/codex`.
6. MCP is **not connected** by this change. It requires a real MCP server, explicit tool permissions, authentication, auditing and sandboxed execution.
7. The AgentActivity panel currently displays **demo events**; connect real worker events before presenting progress as live.

## Constraints
AI Studio does not execute Linux binaries, Codex CLI or native KDE Plasma. Linux-specific integration requires an actual compatible runtime. Do not grant agents host root, automatic shell execution or write access without scoped authorization. No new public API endpoint is exposed for the optional Agents SDK in this commit.

# Mara_OS — AGENTS.md

This file gives GitHub Copilot coding agents and other repository assistants instructions for working with the **Mara_OS** project. It does **not** by itself connect or authenticate external AI agents.

## Project and scope

- GitHub owner: `u6930438163-code`
- Repository: `u6930438163-code/Mara_OS`
- Target branch: `main` (respect GitHub's branch protections and Copilot's PR workflow; never force-push)
- Target platform: Debian 13 / KDE Plasma
- UI: React/Vite (`src/main.jsx`)
- Backend: Python (`server.py`)
- Existing AI adapter: `services/ai.py`
- Existing worker and sync modules: `services/agent_workers.py`, `services/worker_registry.py`, `services/global_sync.py`
- Existing Ollama manager: `services/ollama_manager.py`, `src/OllamaManager.jsx`

## Named Mara_OS agents

| Agent | Identity | Integration requirement |
| --- | --- | --- |
| **Aria** | Named Mara_OS AI agent | Persistent conversation, task queue, worker, tool access, agent-to-agent messages |
| **Alex** | Named Mara_OS AI agent | Persistent conversation, task queue, worker, tool access, agent-to-agent messages |
| **Astyria** | Named Mara_OS AI agent | Persistent conversation, task queue, worker, tool access, agent-to-agent messages |
| **Aurelius** | Named Mara_OS AI agent | Persistent conversation, task queue, worker, tool access, agent-to-agent messages |

**Important:** These names are the desired agent identities, not proof that four independent running agents or external API endpoints currently exist. Discover actual connections before claiming integration. Do not replace the owner's existing agents with simulated responses or four Copilot bots. If existing external agent instances cannot be discovered, build adapters and clearly document the missing endpoint/authentication information.

## Mission for Copilot and contributors

1. Audit existing code and distinguish implemented behavior from demo UI and unverified integrations.
2. Establish an **Agent Runtime** with durable per-agent identity, conversation history, tasks, execution status and worker lifecycle. Persist events and recover pending work on restart.
3. Use the existing `services/ai.py` adapter: Ollama first, Gemini fallback when configured. Vision model: Llama 3.2 Vision 11B; requested text model: Floppa 12B Gemma3 Uncensored Q8_0. Verify actual model availability instead of assuming it.
4. Implement a GitHub bridge scoped initially to `u6930438163-code/Mara_OS`, with repository read/write, issues, PRs and CI status using a GitHub App or narrowly scoped credentials.
5. Expose authenticated MCP/API tools: `list_agents`, `get_agent_status`, `send_agent_message`, `create_agent_task`, `get_agent_task_status`, `get_agent_logs`, `list_agent_workers`.
6. Connect the React chat and dashboards to real agent/runtime data. Support channels `Wszyscy`, `Aria`, `Alex`, `Astyria`, `Aurelius`, durable messages and server-initiated notifications via SSE or WebSocket.
7. Add a controlled tool dispatcher for terminal, Python, files, diagnostics, GitHub, Ollama and MCP. Log commands and actual exit codes; request explicit approval for destructive or privilege-escalating actions.
8. Test end-to-end: user → Aria → worker → authorized tool → result → Aria → user, then repeat for Alex, Astyria and Aurelius. Include failure, recovery and provider fallback tests.

## Security and operational constraints

- Never commit API keys, GitHub tokens, passwords or session tokens. Use environment secrets.
- Use least-privilege GitHub permissions and explicit authorization before expanding beyond Mara_OS.
- No automatic force-push, bypass of branch protection, or silent destructive system actions.
- Do not claim a model, worker, GitHub integration or system command is working without a real test.
- Keep a report of changed files, commits, tests, remaining blockers and setup steps.
- Respect that GitHub Copilot Coding Agent may require a PR rather than direct writes to `main`.

## Initial setup and verification

Read `README.md` for the development start commands. The backend needs `MARA_SESSION_TOKEN`; the frontend uses the Vite `/api` proxy. A running local Ollama service or configured fallback is required for live AI replies. A React prototype is **not** an installable Debian ISO.

**Definition of done:** all four named agents have verified runtime identities, authenticated tool access, real message exchange and working task execution, with tests and no fabricated status reports.

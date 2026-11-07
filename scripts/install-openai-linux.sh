#!/usr/bin/env bash
set -Eeuo pipefail
# Run from Mara_OS repo root. No sudo or global pip installation.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if ! command -v python3 >/dev/null 2>&1; then echo "Python 3 is required" >&2; exit 1; fi
python3 -m venv .venv-ai
.venv-ai/bin/python -m pip install --upgrade pip
.venv-ai/bin/python -m pip install -r requirements-ai.txt
echo "OpenAI + Agents SDK installed into .venv-ai"
echo "Set OPENAI_API_KEY in server environment (never commit secrets)."
echo "Optional Codex CLI: npm install -g @openai/codex (requires supported Node/npm)."
echo "MCP integration needs a separately configured and permissioned MCP server."

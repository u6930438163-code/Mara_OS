# Mara_OS Agents API

Authenticated endpoints on the existing Python server:

- `GET /api/agents/status` returns the four agent names, whether the optional Agents SDK and OpenAI key are available, and whether workers are implemented (currently false).
- `POST /api/agents/run` accepts `{"agent":"Aria","message":"Przywitaj się"}` and returns a synchronous text response from the tool-free OpenAI Agents SDK adapter.

Both require `Authorization: Bearer $MARA_SESSION_TOKEN`. Requests to run are limited to 16 KiB and message length to 8000 characters. Secrets belong only on the server. Never embed API keys in the frontend.

Example from the same trusted Linux host:

```bash
curl -fsS http://127.0.0.1:8765/api/agents/status -H "Authorization: Bearer $MARA_SESSION_TOKEN"
curl -fsS http://127.0.0.1:8765/api/agents/run -H "Authorization: Bearer $MARA_SESSION_TOKEN" -H 'Content-Type: application/json' -d '{"agent":"Aria","message":"Podaj swój status"}'
```

Setup: `bash scripts/install-openai-linux.sh`, set `OPENAI_API_KEY` and `MARA_SESSION_TOKEN`, run `python3 server.py` in the configured environment. The Agents SDK is optional at import time and required to run the Agents API. **Not tested on a live server yet.** There is no background worker, streaming, Linux command execution, MCP or autonomous agent action in this initial endpoint.

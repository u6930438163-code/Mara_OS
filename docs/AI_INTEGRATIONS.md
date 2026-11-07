# Mara_OS — AI integrations

This is a foundation for real integrations, not an autonomous operating system.

## OpenAI
`services/ai.py` provides `ask_agent` for Aria, Alex, Astyria and Aurelius. All four share the same permissions and model access. No Gemini and no deterministic response engine. API credentials remain on the server.

## Real Vision
`analyze_image` accepts JPEG/PNG/WEBP base64 data URLs and uses an OpenAI vision-capable model. It is for analysis of screenshots and images. The API endpoint and file-upload UI still need wiring.

## GitHub
`services/github_read.py` performs read-only repository metadata lookup via the official GitHub REST API. A `GITHUB_TOKEN` may be set server-side for private repositories. No write, merge, issue creation, or automatic actions are implemented.

## MCP
The existing Mara_OS architecture includes MCP as a future integration target. An MCP server/client is **not implemented** here. Implement an authenticated tool registry and explicit approvals before enabling tool execution.

## Security
Do not expose the development server to the internet. Require real user authentication, per-user quotas, request-size limits, CSRF protection and audit logs before production. OpenAI API calls can incur charges. No agent has root or unrestricted GitHub permissions.

## Remaining work
Wire backend routes, frontend forms and logs; implement agent workers, MCP transport, authentication, GitHub write approval flows, and integration tests with mocked providers.

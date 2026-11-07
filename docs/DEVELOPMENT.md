# Mara_OS — development

## Start locally
Requires Python 3.12+ and Node 22+.

```sh
python -m unittest discover -s tests -v
npm install
npm run build
```

Backend needs `MARA_SESSION_TOKEN` (random private value) and `OPENAI_API_KEY` for DALL·E 3. Never commit secrets. Start `python server.py` in one terminal and `npm run dev` in another. Vite proxies `/api` to port 8765.

## Current limitations
- This is an **application prototype**, not a bootable Debian distribution.
- The task queue service is persistent and claim-safe but has no connected agent workers.
- The frontend task list and chat are currently demonstrations, not linked to the persistent task queue.
- DALL·E 3 calls incur API costs. The current backend has no per-user quota or rate limiter and should only run on a trusted local development machine; do not expose it publicly.
- Browser authentication uses a manually entered development token; production needs a proper session-based authentication design.
- No Samsung or Google Photos account access is configured.
- Violet Blade wallpaper is not yet bundled; supply a user-approved licensed image asset.

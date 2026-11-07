# Mara_OS — DALL·E 3 only

Mara_OS uses **DALL·E 3 exclusively for AI image generation**. UI interactivity is implemented in React/CSS/SVG; generated images are assets, never substitutes for real controls.

## Included
- `services/dalle3.py`: server-side OpenAI Images API adapter; validates prompt and DALL·E 3 parameters.
- `ui/Dalle3Studio.jsx` and `ui/dalle3-studio.css`: interactive Violet Blade studio.
- No Gemini and no other image model fallback.

## Required integration before production
1. Mount `Dalle3Studio` inside the Mara_OS React application.
2. Implement an **authenticated** `POST /api/images/generate` backend endpoint accepting `{prompt,size,quality,style}`, calling `generate_image` from `services/dalle3.py`, and returning its result.
3. Apply server-side rate limits, quotas, audit logging without secrets, and CSRF protection as appropriate.
4. Configure `OPENAI_API_KEY` **only in server environment secrets**.
5. Download and store generated images in an authorized asset store if long-term use is required; OpenAI returned URLs expire.
6. Do not overwrite the user's existing Violet Blade wallpaper without approval.

**Status:** Adapter and UI component implemented. API route, app mounting, credentials, deployment, and live generation **not yet implemented or verified**.

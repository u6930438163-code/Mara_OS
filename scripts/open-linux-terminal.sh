#!/usr/bin/env bash
set -Eeuo pipefail
# Native, unrestricted interactive Linux shell in the user's own KDE session.
# Unlike Mara's diagnostic adapters, this is a real terminal emulator.
if ! command -v konsole >/dev/null 2>&1; then
  echo "KDE Konsole is missing. Install with: sudo apt install konsole" >&2
  exit 127
fi
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "No graphical session. For CLI use your current SSH/TTY shell." >&2
  exit 1
fi
exec konsole --workdir "${HOME}" -e "${SHELL:-/bin/bash}" -l

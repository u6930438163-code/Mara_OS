#!/usr/bin/env bash
# Safe preparation helper: prints instructions by default; does not install packages.
set -euo pipefail
if [[ "${1:-}" != "--install" ]]; then
  cat <<'TXT'
Mara_OS KDE Plasma 6 / Debian 13 preparation
Run in a disposable Debian 13 VM first.
Review: sudo apt update && sudo apt install kde-plasma-desktop sddm
This helper makes NO changes without --install.
TXT
  exit 0
fi
if [[ "${ID:-}" != "" ]]; then :; fi
source /etc/os-release
if [[ "${ID:-}" != "debian" || "${VERSION_ID:-}" != "13" ]]; then
  echo "Requires Debian 13; refusing to proceed." >&2
  exit 1
fi
echo "This installs KDE Plasma and SDDM. Confirm manually with apt."
sudo apt update
sudo apt install kde-plasma-desktop sddm
echo "Installation requested. Choose Plasma at login and test before production deployment."

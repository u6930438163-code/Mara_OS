#!/usr/bin/env bash
set -Eeuo pipefail
# Debian 13 host installation; no commands are executed by AI agents.
if [[ $(id -u) -ne 0 ]]; then
  echo "Run with sudo: sudo bash scripts/install-linux-terminal.sh" >&2
  exit 1
fi
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  if [[ "${ID:-}" != "debian" || "${VERSION_ID:-}" != "13" ]]; then
    echo "This installer targets Debian 13." >&2
    exit 1
  fi
fi
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y konsole bash bash-completion sudo coreutils util-linux procps iproute2 openssh-client git curl python3
echo "KDE Konsole and common Linux CLI utilities installed."
echo "Launch Konsole from KDE menu or run: bash scripts/open-linux-terminal.sh"
echo "GParted (GUI) and parted (CLI) are separate optional packages."

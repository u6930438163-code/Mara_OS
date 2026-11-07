#!/usr/bin/env bash
set -Eeuo pipefail
# Install GParted from the configured Debian 13 repositories.
# Run on the target Debian 13 machine as root; no partition changes are performed.
if [[ $(id -u) -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/install-gparted.sh" >&2
  exit 1
fi
if ! command -v apt-get >/dev/null 2>&1; then
  echo "APT is required (Debian 13)." >&2
  exit 1
fi
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  if [[ "${ID:-}" != "debian" || "${VERSION_ID:-}" != "13" ]]; then
    echo "This installer targets Debian 13; detected ${PRETTY_NAME:-unknown}." >&2
    exit 1
  fi
fi
apt-get update
candidate="$(apt-cache policy gparted | awk '/Candidate:/ {print $2; exit}')"
if [[ -z "$candidate" || "$candidate" == "(none)" ]]; then
  echo "No GParted candidate in configured APT repositories." >&2
  exit 1
fi
echo "Installing official Debian GParted candidate: $candidate"
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gparted
echo "GParted installed. Launch from KDE menu or run: gparted"
echo "No partition operations have been performed."

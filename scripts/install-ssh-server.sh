#!/usr/bin/env bash
set -Eeuo pipefail
# Debian 13: install and enable SSH server on boot.
# Does not alter firewall rules or expose the host through a router.
if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run: sudo bash scripts/install-ssh-server.sh" >&2
  exit 1
fi
if [[ ! -r /etc/os-release ]]; then
  echo "Cannot verify operating system." >&2
  exit 1
fi
. /etc/os-release
if [[ "${ID:-}" != "debian" || "${VERSION_ID:-}" != "13" ]]; then
  echo "This installer supports Debian 13 only." >&2
  exit 1
fi
if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemd is required to enable SSH at boot." >&2
  exit 1
fi
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-server
install -d -m 0755 /etc/ssh/sshd_config.d
# Disable remote root login; keep standard user authentication unchanged
# to avoid locking out an administrator without SSH keys.
printf '%s\n' '# Mara_OS SSH baseline' 'PermitRootLogin no' > /etc/ssh/sshd_config.d/60-mara-os.conf
chmod 0644 /etc/ssh/sshd_config.d/60-mara-os.conf
if ! /usr/sbin/sshd -t; then
  echo "SSH configuration invalid; service was not enabled." >&2
  exit 1
fi
systemctl enable --now ssh.service
systemctl reload ssh.service
systemctl --no-pager --full status ssh.service || true
echo "SSH server enabled on boot. Check firewall, authorized users and network exposure."
echo "For remote access, use: ssh USER@HOST_IP"

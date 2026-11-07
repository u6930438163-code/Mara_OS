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
# Root-only SSH is explicitly requested by the owner. Never embed passwords.
# A root password must be set interactively on the target host.
if [[ ! -t 0 ]]; then
  echo "Interactive terminal required to set the root password safely." >&2
  exit 1
fi
echo "Set the root account password locally (input is hidden)."
passwd root
printf '%s\n' '# Mara_OS root-only SSH' 'PermitRootLogin yes' 'PasswordAuthentication yes' 'AllowUsers root' > /etc/ssh/sshd_config.d/00-mara-os.conf
chmod 0644 /etc/ssh/sshd_config.d/00-mara-os.conf
# Remove the previous Mara_OS drop-in to avoid conflicting first-value-wins settings.
rm -f /etc/ssh/sshd_config.d/60-mara-os.conf
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! bash "$SCRIPT_DIR/check-ssh-config.sh"; then
  echo "Effective SSH policy verification failed; service not enabled by this installer." >&2
  exit 1
fi
systemctl enable --now ssh.service
systemctl reload ssh.service
systemctl --no-pager --full status ssh.service || true
echo "SSH server enabled on boot. Check firewall, authorized users and network exposure."
echo "For remote access, use: ssh root@HOST_IP"

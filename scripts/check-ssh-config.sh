#!/usr/bin/env bash
set -Eeuo pipefail
# Verify the effective SSH policy; sshd -t alone checks only syntax.
if [[ "$(id -u)" -ne 0 ]]; then echo "Run with sudo" >&2; exit 1; fi
/usr/sbin/sshd -t
effective=$(/usr/sbin/sshd -T -C user=root,host=localhost,addr=127.0.0.1)
for setting in "permitrootlogin yes" "passwordauthentication yes" "allowusers root"; do
  if ! grep -Fxq "$setting" <<<"$effective"; then
    echo "SSH effective configuration mismatch: $setting" >&2
    exit 1
  fi
done
if grep -Eq '^allowusers .* ' <<<"$effective"; then
  echo "More than one SSH user allowed; refusing to proceed." >&2
  exit 1
fi
echo "SSH effective root-only policy verified for local connection context."
echo "Note: Match blocks can alter policy for other remote addresses; review sshd -T -C with actual client address."

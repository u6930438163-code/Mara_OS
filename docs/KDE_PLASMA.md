# Mara_OS — KDE Plasma 6 (Debian 13)

## Goal
KDE Plasma 6 is the desktop environment. The existing Mara_OS React interface remains the control center, launched as a desktop app or in a browser. The owner and Aria, Alex, Astyria, Aurelius use **one common theme and UI codebase**; accounts and data are isolated.

Debian 13 Trixie ships Plasma 6.3. The `kde-plasma-desktop` package provides the minimal desktop; `sddm` provides login. Start with a test VM, not the production host.

## Deployment sequence
1. Create a Debian 13 test VM or snapshot. Install Plasma with `sudo apt update && sudo apt install kde-plasma-desktop sddm` after reviewing the packages.
2. Log into a test user with Plasma Wayland; verify hardware graphics and screen sharing.
3. Install Mara_OS frontend as a launcher/web app in the KDE menu. Keep the existing CSS, wallpaper and theme tokens.
4. Provision four isolated, non-admin accounts (Aria, Alex, Astyria, Aurelius). Use a centrally maintained, read-only theme distribution for all users. Do not share home directories or browser profiles.
5. Attach per-agent sandboxed workers and explicitly permissioned desktop control tools. Remote observation must be authenticated and access-controlled.
6. Only after tests, enable remote desktop viewing and optional controlled interactions. Wayland screen capture/input requires compositor-supported mechanisms; X11-oriented automation should not be assumed to work.

## Security and limitations
- Do not give AI agents unrestricted host root, direct access to owner credentials, or a shared browser profile.
- Never expose RDP/VNC directly to the public internet; prefer a VPN and authenticated gateway.
- GitHub writes, shell execution, purchases and privileged actions require explicit permission policies and audit trails.
- A matching theme does **not** mean the agents have active KDE sessions. Those require actual host/VM deployment.
- This repository currently contains a UI prototype and backend adapters, not a bootable Debian distribution.

## Appearance parity
Keep one version-controlled Mara_OS wallpaper, color palette, fonts, Plasma global theme, icons, window decorations and launcher configuration. The agent identity may change name/avatar but not the shared visual theme. Avoid modifying the user's existing KDE configuration without backup.

## Acceptance criteria
- Five accounts have matching desktop appearance after fresh login.
- Each account has isolated files, secrets and browser sessions.
- Owner can observe agent session with an explicit authorization boundary.
- Agent can launch Mara_OS and use only allowed applications.
- Remote sessions and workers recover from logout/reboot without compromising isolation.

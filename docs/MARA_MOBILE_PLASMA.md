# Mara_OS — Bastilla_1_2 layout + KDE Plasma 6.8.2 target

## Version decision
Target upstream KDE Plasma version: **6.8.2** (owner selection, 2026-11-07). This is a target, not an installed or validated package. Debian 13 stock repositories may provide an older Plasma release; do not assume 6.8.2 can be installed via standard apt. Validate package availability, compatibility and device support before any deployment. Do not silently substitute an older version.

## Decision
Target phones: Huawei P Smart 2019 and Samsung Galaxy A13 SM-A135F (model to confirm). User wants the **real, complete KDE Plasma**, with Mara_OS's Bastilla_1_2-inspired look, developed through Google AI Studio.

## Two distinct deliverables
1. **AI Studio preview:** responsive React Mara_OS shell, launcher, windows, panel, chat, agent desktops and integrations. This is a useful prototype and is **not** KDE Plasma itself.
2. **Native KDE runtime:** KWin, Plasma Workspace, Qt 6, KDE Frameworks, Dolphin, Konsole, System Settings and session management running on Linux. Native runtime requires hardware-specific kernel/graphics/input integration, which AI Studio cannot provide.

## Device feasibility gates
- Confirm exact Samsung model, chipset and Android/build versions.
- Research a maintained Linux device port for each exact hardware variant, bootloader unlock constraints, GPU acceleration, touch, Wi-Fi, audio, modem, suspend and battery.
- Do not flash, repartition or unlock a phone before backups, compatibility validation and explicit approval.
- If native support is absent, label the blocker; do not present a browser simulation as full Plasma.
- Performance targets: mobile touch targets, low-memory rendering, keyboard/rotation support.

## Work packages
- [x] React Mobile Plasma preview with launcher, panel, movable navigation and window minimize/close interactions.
- [ ] Align shared Bastilla_1_2 styling and wallpaper with owner's approved assets.
- [ ] Validate React build and mobile behavior on both devices.
- [ ] Verify native Linux + Plasma feasibility for each exact phone.
- [ ] Build KDE Plasma global theme, KWin configuration, icons, desktop launchers and Qt Quick touch layout.
- [ ] Run and test native KDE session on actual supported hardware.
- [ ] Connect agent services with per-agent isolation and audited permissions.

## Nonclaims
No native KDE installation, hardware boot, live agent sessions, or real terminal execution has been verified.

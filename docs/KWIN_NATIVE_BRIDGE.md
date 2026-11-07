# Mara_OS — KDE KWin native window integration

The next integration boundary is **KWin 6 on Wayland**, not the Linux kernel. KDE's window manager owns native window placement and minimization.

## Implemented now

- `services/kwin_bridge.py`: converts a desktop activity profile into a **dry-run** native window plan.
- Only app IDs explicitly passed as `managed` are eligible for the plan. Unmanaged windows are never touched.
- Pinned Mara_OS panels are excluded from minimization.
- `GET /api/desktop/kwin-plan?activity=diagnostics&managed=org.kde.konsole&managed=org.kde.dolphin` returns a plan with `applied: false`.
- `tests/test_kwin_bridge.py` tests managed-only, pinned, and invalid-activity cases.

## Why no direct native window changes yet?

The web backend may run without a graphical session. KWin scripting is session-specific, and the KWin 6 API must be validated against the Debian 13 Plasma version. A root/system service should **not** attempt to control another user's Wayland session. Native changes need a separate per-user KWin script/plugin, an authenticated session IPC channel, and verified app/window identities.

## Next implementation

1. Confirm KWin/Plasma versions on the target Debian 13 machine.
2. Install a user-session KWin script/plugin and use its supported API to identify Mara_OS-owned windows.
3. Add an opt-in IPC link from the layout planner to the user-session component.
4. Implement show/raise/minimize, never destructive close, with pinning and an emergency manual override.
5. Run integration tests in an actual Plasma Wayland session.

No native KDE control, system deployment, or root permission changes are claimed.

"""KWin bridge preparation: map Mara_OS layout intentions to managed KDE windows.

This module intentionally produces a plan only. KWin scripting/DBus requires
a live KDE user session; arbitrary window titles and shell commands are rejected.
"""
from services.desktop_planner import plan

# Stable app IDs, not substring matching against arbitrary window titles.
APP_IDS = {
    "chat": ("org.maraos.Chat",),
    "terminal": ("org.kde.konsole",),
    "logs": ("org.maraos.Logs",),
    "workers": ("org.maraos.Workers",),
    "files": ("org.kde.dolphin",),
    "resources": ("org.kde.plasma-systemmonitor",),
}

def native_plan(activity, pinned=(), managed_app_ids=()):
    layout = plan(activity, pinned=pinned)
    managed = set(managed_app_ids)
    if any(not isinstance(app, str) for app in managed):
        raise ValueError("Invalid app ID")
    show = [app for window in layout["visible"] for app in APP_IDS[window] if app in managed]
    hide = [app for window in layout["hidden"] for app in APP_IDS[window] if app in managed]
    return {
        "activity": activity,
        "show_app_ids": show,
        "minimize_app_ids": hide,
        "pinned": list(pinned),
        "requires_session": "KWin 6 Wayland",
        "applied": False,
        "note": "Only previously registered Mara_OS-managed windows may be minimized; never close applications.",
    }

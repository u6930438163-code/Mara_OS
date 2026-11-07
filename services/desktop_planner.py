"""Deterministic, testable UI layout planner for Mara_OS live panels.

It only emits UI intents, never executes shell commands or controls native windows.
"""
from services.live_desktop import WINDOWS

PROFILES = {
    "idle": ("chat",),
    "chat": ("chat", "workers"),
    "diagnostics": ("terminal", "logs", "resources"),
    "development": ("terminal", "files", "logs"),
    "monitoring": ("resources", "workers", "logs"),
}

def plan(activity, pinned=(), available=WINDOWS):
    if activity not in PROFILES:
        raise ValueError("Unknown activity")
    allowed = set(available)
    if not allowed.issubset(set(WINDOWS)):
        raise ValueError("Unknown window")
    pinned = tuple(pinned)
    if not set(pinned).issubset(allowed):
        raise ValueError("Unknown pinned window")
    visible = list(dict.fromkeys([*pinned, *(w for w in PROFILES[activity] if w in allowed)]))
    return {
        "activity": activity,
        "visible": visible,
        "hidden": [w for w in available if w not in visible],
        "pinned": list(pinned),
        "mode": "recommendation",
    }

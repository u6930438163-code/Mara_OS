"""Read-only Linux kernel capabilities and resource diagnostics for Mara_OS.

Uses supported procfs/sysfs/cgroup v2 interfaces. Never writes kernel parameters.
"""
from pathlib import Path
import json
import os

def read(path, limit=4096):
    try:
        return Path(path).read_text(errors="replace")[:limit].strip()
    except (OSError, ValueError):
        return None

def available_governors():
    root = Path("/sys/devices/system/cpu/cpufreq")
    result = {}
    if root.exists():
        for policy in sorted(root.glob("policy*"))[:64]:
            result[policy.name] = {
                "current": read(policy / "scaling_governor"),
                "available": (read(policy / "scaling_available_governors") or "").split(),
            }
    return result

def cgroup():
    root = Path("/sys/fs/cgroup")
    return {
        "v2": (root / "cgroup.controllers").exists(),
        "controllers": (read(root / "cgroup.controllers") or "").split(),
        "memory_current": read(root / "memory.current"),
        "memory_max": read(root / "memory.max"),
        "cpu_max": read(root / "cpu.max"),
        "cpu_pressure": read(root / "cpu.pressure", 1024),
        "memory_pressure": read(root / "memory.pressure", 1024),
    }

def snapshot():
    return {
        "kernel": read("/proc/sys/kernel/osrelease"),
        "kernel_build": read("/proc/version", 1024),
        "loadavg": read("/proc/loadavg"),
        "uptime_seconds": (read("/proc/uptime") or "").split(" ")[0],
        "cgroup": cgroup(),
        "cpu_governors": available_governors(),
        "ebpf": {
            "bpf_filesystem": Path("/sys/fs/bpf").exists(),
            "bpf_jit_enabled": read("/proc/sys/net/core/bpf_jit_enable"),
            "unprivileged_bpf_disabled": read("/proc/sys/kernel/unprivileged_bpf_disabled"),
        },
        "interfaces": {
            "vfs": True,
            "sysfs": Path("/sys").exists(),
            "procfs": Path("/proc").exists(),
        },
        "mode": "read_only",
    }

if __name__ == "__main__":
    print(json.dumps(snapshot(), ensure_ascii=False, indent=2))

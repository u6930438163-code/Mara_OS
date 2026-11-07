"""Adaptive worker concurrency policy from Linux pressure and load.

Policy only: does not change kernel settings, privileges or cgroups.
"""
import os
from services.kernel_adaptation import snapshot

def pressure_avg10(value):
    if not value:
        return None
    for line in value.splitlines():
        if line.startswith("some "):
            for field in line.split():
                if field.startswith("avg10="):
                    try:
                        return float(field.split("=", 1)[1])
                    except ValueError:
                        return None
    return None

def recommend_limits(data=None, max_workers=8):
    data = snapshot() if data is None else data
    max_workers = max(1, min(int(max_workers), 32))
    cpu = pressure_avg10(data.get("cgroup", {}).get("cpu_pressure"))
    memory = pressure_avg10(data.get("cgroup", {}).get("memory_pressure"))
    try:
        load = float((data.get("loadavg") or "").split()[0])
    except (ValueError, IndexError):
        load = None
    cores = os.cpu_count() or 1
    reasons = []
    target = max_workers
    if memory is not None and memory >= 25:
        target = min(target, 1)
        reasons.append("high memory pressure")
    elif memory is not None and memory >= 10:
        target = min(target, max(1, max_workers // 2))
        reasons.append("moderate memory pressure")
    if cpu is not None and cpu >= 50:
        target = min(target, max(1, max_workers // 2))
        reasons.append("high cpu pressure")
    if load is not None and load > cores * 2:
        target = min(target, max(1, max_workers // 2))
        reasons.append("high system load")
    return {
        "recommended_workers_per_agent": target,
        "configured_max": max_workers,
        "cpu_pressure_avg10": cpu,
        "memory_pressure_avg10": memory,
        "load_1m": load,
        "cpu_count": cores,
        "reasons": reasons or ["normal load"],
        "applied": False,
    }

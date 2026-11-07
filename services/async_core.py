"""Bounded asynchronous core coordinator for Mara_OS.

This module intentionally does not run shell commands or external actions.
It provides task lifecycle and measured status for trusted internal adapters.
"""
import asyncio
import time
import uuid
from dataclasses import dataclass, field

PROFILES = {
    "chat": {"priority": 0, "timeout": 90},
    "diagnostics": {"priority": 10, "timeout": 60},
    "github": {"priority": 15, "timeout": 120},
    "images": {"priority": 20, "timeout": 180},
    "desktop": {"priority": 25, "timeout": 60},
}
AGENTS = frozenset(("Aria", "Alex", "Astyria", "Aurelius"))

@dataclass
class Job:
    id: str
    agent: str
    kind: str
    state: str = "pending"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    result: object = None
    error: str = ""
    events: list = field(default_factory=list)

    def event(self, state, message):
        self.state = state
        self.updated_at = time.time()
        self.events.append({"time": self.updated_at, "state": state, "message": message})

class AsyncCore:
    """In-process bounded coordinator; no persistence or crash recovery yet."""

    def __init__(self, workers=2, max_pending=100):
        if workers < 1 or max_pending < 1:
            raise ValueError("Positive worker and queue limits required")
        self.queue = asyncio.PriorityQueue(maxsize=max_pending)
        self.workers = workers
        self.jobs = {}
        self.handlers = {}
        self._tasks = []
        self._seq = 0

    def register(self, kind, handler):
        if kind not in PROFILES or not asyncio.iscoroutinefunction(handler):
            raise ValueError("Registered handler must be async and use a known profile")
        self.handlers[kind] = handler

    async def start(self):
        if self._tasks:
            return
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.workers)]

    async def submit(self, agent, kind, payload):
        if agent not in AGENTS or kind not in self.handlers:
            raise ValueError("Unknown agent or unavailable task handler")
        if self.queue.full():
            raise RuntimeError("Core queue is full")
        job = Job(id=uuid.uuid4().hex, agent=agent, kind=kind)
        job.event("pending", "Queued")
        self._seq += 1
        self.queue.put_nowait((PROFILES[kind]["priority"], self._seq, job.id, payload))
        self.jobs[job.id] = job
        return job.id

    async def _worker(self):
        while True:
            _, _, job_id, payload = await self.queue.get()
            job = self.jobs[job_id]
            try:
                job.event("running", "Started")
                job.result = await asyncio.wait_for(
                    self.handlers[job.kind](job.agent, payload),
                    timeout=PROFILES[job.kind]["timeout"])
                job.event("done", "Completed")
            except asyncio.CancelledError:
                job.event("cancelled", "Worker stopped")
                raise
            except Exception as exc:
                job.error = type(exc).__name__
                job.event("failed", "Execution failed")
            finally:
                self.queue.task_done()

    async def shutdown(self):
        tasks, self._tasks = self._tasks, []
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

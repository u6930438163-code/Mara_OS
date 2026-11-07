# Mara_OS core: asynchronous and asymmetric architecture

## Binding decision
The **whole Mara_OS core**, not only OpenAI agents, must use asynchronous boundaries where practical. Asymmetry means per-module resource limits, priorities, permissions and execution profiles; it does not mean unequal standing for Aria, Alex, Astyria and Aurelius.

## Core boundaries
- **UI / AI Studio**: nonblocking rendering, optimistic pending states, real event-driven progress, cancellable requests.
- **API gateway**: authenticated submissions; returns task IDs immediately, no long-running work on HTTP request threads.
- **Durable queue**: SQLite initially; persisted state pending/running/done/failed, retry budgets, leases and recovery after restart.
- **Worker pools**: separate AI inference, diagnostics, GitHub, files and desktop tasks; per-agent quotas and bounded concurrency.
- **Event journal**: append-only per-task status, timestamps, stage descriptions, stdout/stderr (redacted), error codes and correlation IDs.
- **Agent messages**: async inbox/outbox with sender/recipient, ordering per conversation and explicit authorization.
- **KDE runtime**: native Plasma/KWin must run on compatible Linux; expose events via authenticated adapters, not by pretending the React shell is native Plasma.
- **Phones**: responsive, low-memory frontend; no long-running background execution assumed inside AI Studio/browser.

## Asymmetric execution profiles
Interactive chat: high priority, small payloads and short timeouts.
Diagnostics: read-only by default, bounded output and CPU.
Code/repository tasks: isolated workspace, audit and explicit write authorization.
Image generation: lower priority and strict cost/rate limits.
Desktop control: explicit per-session approval, restricted capabilities.
All four agents share the same interface and base policy; task profiles differ by workload, not by agent identity.

## Safety and correctness
- Never claim progress percentages without a measured step count; show indeterminate progress otherwise.
- Never run arbitrary user-provided shell text via the API.
- Secrets remain server-side; require authorization for actions with side effects.
- Every job has id, owner, type, timestamps, state, attempt count and an audit trail.
- Handle backpressure, cancellation, graceful shutdown, crash recovery and worker isolation.
- Do not grant unrestricted root or expose remote desktops directly.

## Delivery stages
1. Add bounded async task coordinator and status endpoints.
2. Persist jobs/events and recover incomplete work.
3. Connect OpenAI Agents SDK asynchronous runs and real progress events.
4. Connect diagnostics and KDE adapters only on verified Linux runtime.
5. Add mobile UI live status updates and full script/log inspector.

**Current status:** architecture decision and first code components only; native KDE and fully autonomous workers are not deployed.

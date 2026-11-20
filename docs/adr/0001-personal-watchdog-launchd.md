# ADR 0001: Personal watchdog installation via Ansible and launchd

- Status: Accepted
- Date: 2026-11-17
- Related: [Watchdog ADR 0001](https://github.com/BBGrimmett2/MacOS-Config-Watchdog/blob/main/docs/adr/0001-repository-and-phases.md), [Watchdog ADR 0002](https://github.com/BBGrimmett2/MacOS-Config-Watchdog/blob/main/docs/adr/0002-observation-and-state.md)

## Context

The watchdog engine is in a separate repository, and the personal Mac needs
a reproducible, least-privilege way to run its observer on login. Cron and
system-wide privileged daemons are unnecessary for the initial read-only agent.

## Decision

Expose a dedicated, opt-in `playbooks/install_mac_watchdog.yml` which invokes
the `mac_watchdog` role for the personal profile only. Install source from an
immutable commit of the dedicated watchdog repository, using an isolated
Python virtual environment. The source is not executed as a root process.
Install a user LaunchAgent in `~/Library/LaunchAgents`, enabled by launchd's
KeepAlive, RunAtLoad and throttling. The agent runs the watchdog's event-driven
`monitor` command; the daemon handles 30-minute reconciliation. launchd
handles start/restart at user login and process failure. Avoid arbitrary
command execution and avoid scheduled cron jobs.

Installation is **not** added to the master bootstrap without separate
approval. Monitor startup is intentionally limited to the personal Mac. No
automatic Ansible deployment or rollback is enabled here.

## Consequences

Ansible must be invoked in the target user's GUI session. Python >=3.11
and git must be installed. A future release mechanism may replace pinned
source checkout; update this ADR if the distribution model changes.
The Mac wake hook, weekly deep collectors and manifest agreement remain
watchdog-engine follow-up work, not properties of launchd itself.

# ADR 0003: Derive package expectations from installation role settings

- Status: Accepted
- Date: 2026-11-19
- Related: ADR 0002

## Context
The initial personal expected-state export only included common and personal CLI formula lists. The workstation's cloud, Kubernetes, network, development, desktop, database and terminal roles install additional Homebrew formulae and casks. Those appeared unmanaged despite being selected by Ansible.

## Decision
The manifest exporter loads the original role defaults into namespaced dictionaries and combines them with explicit personal-profile overrides, without executing installer roles. An allowlisted Python filter interprets each role's package selection flags, install-all and present/absent settings. It maps package names to the canonical Homebrew inventory identifier (notably kubectl -> kubernetes-cli). Only actual Homebrew-managed items are emitted; non-Homebrew installers, external packages and credentials remain outside the contract. The personal profile is loaded in isolation; never read or include work profile settings.

Keep comparison strictly read-only, schema v1, deterministic and idempotent. This expansion does not infer whether unrelated formulae are dependencies: the watchdog must classify that using local Homebrew installation metadata in a separate change.

## Consequences
Ansible roles remain the source of truth rather than a second package list. Every new role package mapping requires a corresponding allowlist entry and regression test; unsupported modes must fail closed rather than fabricate an expectation.

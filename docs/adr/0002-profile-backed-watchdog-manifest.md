# ADR 0002: Profile-backed personal watchdog manifest

- Status: Accepted
- Date: 2026-11-19

## Context
The watchdog's strict expected-state JSON schema requires an Ansible-owned producer. Duplicating package lists in a separate config file would drift from workstation configuration.

## Decision
Source common and personal CLI formulae from the existing inventory `cli_tools_packages_common` and `cli_tools_packages_extra`. Use an explicit non-secret `mac_watchdog_expected_resources` profile list for resource categories not yet mapped safely to Ansible installation settings. An isolated personal-only role validates inputs and renders a deterministic JSON schema v1 manifest in the local private watchdog state directory, with permissions 0700/0600. The export-only playbook never runs installer roles or changes workstation configuration. Work profiles must not be exported. A Python filter makes data transformation auditable and testable.

## Consequences
Changing a common or personal CLI package list changes the intended formula inventory on next export. Extra resources are manual until role-specific mappings are validated. Only explicitly declared categories are called managed; an absent observation is not proof of missing software. Automated scheduling of manifest export is separate.

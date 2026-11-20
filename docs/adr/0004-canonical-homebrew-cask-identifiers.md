# ADR 0004: Canonical identifiers for Homebrew casks

- Status: Accepted
- Date: 2026-11-19
- Related: ADR 0003

## Context
The personal watchdog expected-state report listed Google Cloud CLI and Wireshark as not observed even though they were installed. Homebrew inventory uses `gcloud-cli` and `wireshark-app`; Ansible retained `google-cloud-sdk` and `wireshark`.

## Decision
Use canonical names consistently in cloud and network role defaults, the Google Cloud installer, and the expected-state filter allowlist. The GCP installer checks the actual cask via `brew list --cask` rather than probing an outdated Intel Caskroom path. Its check is read-only and its installation remains conditional on absence. Keep Azure CLI in expected state because it is genuinely absent and enabled.

## Consequences
The two installed casks will match the next exported manifest without reinstalling them. Changes to Homebrew package names must be validated in both installation and expected-state paths.

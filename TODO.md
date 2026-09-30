# TODO

Authoritative list of open work items. Confirmed against actual code — planning-phase checkboxes in `docs/planning/workstation_setup_plan.md` are excluded as those implementations exist.

---

## Role / Task Gaps — Blocks Playbook Runs

| Status | Item | File | Priority |
|--------|------|------|----------|
| [ ] | Claude Code personal profile setup is a stub — prints manual instructions only | `roles/development_tools/tasks/install_claude_code_personal.yml` | HIGH |

---

## Missing Targeted Playbooks

Per `docs/planning/targeted-playbooks-architecture.md`. Tasks exist in roles but no standalone playbook exposes them for day-to-day use.

| Status | Playbook | Priority | Notes |
|--------|----------|----------|-------|
| [ ] | `playbooks/configure_git.yml` | HIGH | Wraps `roles/development_tools/tasks/configure_git.yml` |
| [ ] | `playbooks/configure_mcp.yml` | HIGH | Wraps `roles/development_tools/tasks/configure_mcp.yml` |
| [ ] | `playbooks/setup_claude_code_work.yml` | HIGH | Extracts VPN pause out of `install_development_tools.yml` |
| [ ] | `playbooks/configure_claude_code.yml` | HIGH | Reconfigure Vertex AI token without VPN |
| [ ] | `playbooks/configure_ssh.yml` | MEDIUM | Refresh SSH keys from Dashlane in isolation |
| [ ] | `playbooks/configure_macos.yml` | MEDIUM | Expose `macos_defaults` sub-tags without running full bootstrap |
| [ ] | `playbooks/deploy_certificates.yml` | MEDIUM | Wrap `roles/network_tools/tasks/deploy_certificates.yml` |
| [ ] | `playbooks/refresh_secrets.yml` | LOW | Chain SSH + gitconfig refresh under one Dashlane validation |

---

## Open GitHub Issues

| Status | Issue | Title | Labels |
|--------|-------|-------|--------|
| [ ] | [#1](../../issues/1) | Dashlane CLI should auto-open browser without manual code copy | enhancement |
| [ ] | [#2](../../issues/2) | PAM Security role requires sudo password during playbook execution | documentation, enhancement |
| [ ] | [#3](../../issues/3) | Add sudoers configuration role for passwordless automation | enhancement |
| [ ] | [#4](../../issues/4) | Fix automated certificate trust installation | bug |
| [ ] | [#5](../../issues/5) | Audit and remove unused variables from role defaults and host_vars | enhancement |
| [ ] | [#6](../../issues/6) | install.sh deletes repo and venv — targeted playbooks have no persistent runtime | enhancement |
| [ ] | [#7](../../issues/7) | VS Code: backup, clean up, and deploy settings via Ansible | enhancement |

---

## CI/CD Workflow Issues

Per `docs/planning/github-workflows-review.md`.

### Bugs in Existing Workflows

| Status | Workflow | Issues |
|--------|----------|--------|
| [ ] | `.github/workflows/validate.yml` | `yamllint` commented out; `markdownlint` commented out; ShellCheck installed but never called; `--syntax-check` missing `-i` flag; triggers on `master` instead of `main` |
| [ ] | `.github/workflows/spotter-ci.yml` | Triggers on all branches; outdated `actions/checkout@v3`; hard-coded `ansible-core==2.16`; no guard for missing `SPOTTER_TOKEN` |
| [ ] | `.github/workflows/build-execution-environment.yml` | `ansible-builder` version unpinned; unsanitized user input in shell; no pre-build validation; no image vulnerability scan |
| [ ] | `.github/workflows/molecule-actions.yml` | Cannot test macOS-specific tasks — recommend deleting |

### New Workflows to Create

| Status | Workflow | Priority |
|--------|----------|----------|
| [ ] | `lint.yml` — unified YAML, Ansible, Shell, Markdown linting | HIGH |
| [ ] | Fix `validate.yml` — repair all 5 bugs above | HIGH |
| [ ] | `security-scan.yml` — secret scanning + dependency review | MEDIUM |
| [ ] | `syntax-check-matrix.yml` — test across multiple ansible-core versions | MEDIUM |
| [ ] | `role-structure-audit.yml` — enforce `AGENTS.md` conventions | LOW |
| [ ] | `ee-validate.yml` — validate execution environment definition changes | LOW |
| [ ] | `release.yml` — auto-generate GitHub releases | LOW |

---

## Backlog / Future

| Status | Item | Notes |
|--------|------|-------|
| [ ] | DMG installer package | Phase 0 of `docs/planning/workstation_setup_plan.md` |
| [ ] | WorkstationManager Swift app | Full spec in `WorkstationManager/README.md`; 5 dev phases not started |
| [ ] | Uninstall / revert strategy | Every role should support `state: absent`; Phase 3 of plan |

---

*Last updated: 2026-09-29. Close items here and in the linked GitHub issue when complete.*

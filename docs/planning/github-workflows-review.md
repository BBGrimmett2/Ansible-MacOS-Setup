# GitHub Workflows Review

**Date:** 2026-09-29
**Scope:** Audit existing workflows and recommend new ones for the Ansible macOS Setup repo.

---

## Overview

This repo automates macOS workstation setup via Ansible roles (Homebrew, Dock, Git, VPN, certificates, development tools, etc.). CI/CD should focus on:

- Linting Ansible, YAML, shell scripts, and Markdown
- Syntax-checking playbooks against multiple Ansible versions
- Validating role structure (enforcing AGENTS.md conventions)
- Secret scanning
- Execution Environment (EE) definition validation
- Automated releases on version tags

Molecule-based testing has limited value here because most tasks are macOS-specific and cannot run in a Linux container.

---

## Existing Workflows — Audit

### 1. `validate.yml`

**Purpose:** Runs `ansible-playbook --syntax-check` and (partially) linting on push/PR to `main`.

**Issues:**

| # | Issue | Fix |
|---|-------|-----|
| 1 | `yamllint` step is commented out — not running | Uncomment or replace with `action-yamllint` |
| 2 | `markdownlint` step is commented out — not running | Uncomment or replace with `articulate/run-markdownlint` |
| 3 | ShellCheck is installed but `shellcheck` is never called | Add an explicit ShellCheck run step |
| 4 | `ansible-playbook --syntax-check` has no `-i` flag — relies on implicit inventory | Add `-i inventories/localhost` |
| 5 | Triggers on `master` branch, which does not exist in this repo | Change to `main` |

**Recommendation:** Fix all five issues rather than replace this workflow.

---

### 2. `spotter-ci.yml`

**Purpose:** Runs the Spotter CI integration (custom CI tooling).

**Issues:**

| # | Issue | Fix |
|---|-------|-----|
| 1 | Triggers on all pushes to all branches — noisy and wasteful | Scope to `main` and PRs |
| 2 | Uses `actions/checkout@v3` (outdated) | Upgrade to `actions/checkout@v4` |
| 3 | Hard-codes `ansible-core==2.16` | Parameterize or pin to a range |
| 4 | No guard if `SPOTTER_TOKEN` secret is missing — will fail opaquely | Add a pre-check step |

---

### 3. `build-execution-environment.yml`

**Purpose:** Builds and pushes an Ansible Execution Environment container image.

**Issues:**

| # | Issue | Fix |
|---|-------|-----|
| 1 | `ansible-builder` is not pinned to a version — will break when v4 releases | Pin: `pip install ansible-builder==3.*` |
| 2 | User-supplied `inputs.tag` is interpolated directly into shell without sanitization | Validate input or use `--tag` flag with proper quoting |
| 3 | No pre-build validation (`ansible-builder create`) on PRs | Add cheap validation step before full build |
| 4 | No vulnerability scan of the built image | Add `aquasecurity/trivy-action` after build |
| 5 | Summary message says `podman pull` but workflow uses Docker | Fix summary text |

---

### 4. `molecule-actions.yml`

**Purpose:** Runs Molecule tests.

**Issues:**

| # | Issue | Fix |
|---|-------|-----|
| 1 | `working-directory` points to `collections/ansible_collections/sample_namespace/github_action_sample/extensions` — path does not exist in this repo | N/A |
| 2 | Targets `dev`/`prod` branches that don't exist | N/A |
| 3 | Uses `actions/checkout@v2` (severely outdated) | N/A |
| 4 | Molecule with Docker/Fedora cannot test macOS-specific tools (Homebrew, Dock, Keychain, etc.) | N/A |

**Recommendation: Delete this workflow.** It has never run successfully against this repo and cannot provide meaningful test coverage for macOS-specific automation.

---

## Recommended New Workflows

### Priority 1 — `lint.yml` (replaces scattered lint in `validate.yml`)

Unified linting across all content types in separate jobs for clear failure attribution.

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  yaml-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ibiqlik/action-yamllint@v3
        with:
          config_file: .yamllint

  ansible-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ansible-lint
      - run: ansible-lint

  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ludeeus/action-shellcheck@master
        with:
          scandir: './scripts'

  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: articulate/actions-markdownlint@v1

  spellcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: streetsidesoftware/cspell-action@v6
```

**Supporting files needed:** `.yamllint`, `.cspell.json`

---

### Priority 2 — Fix `validate.yml`

Apply the five fixes listed in the audit above. No new workflow needed — just repair the existing one.

---

### Priority 3 — `security-scan.yml`

Secret scanning and dependency review to catch credential leaks and vulnerable dependencies.

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
```

---

### Priority 4 — `syntax-check-matrix.yml`

Validates all playbooks across multiple ansible-core versions to catch compatibility issues early.

```yaml
name: Syntax Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  syntax-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        ansible-core: ['2.16', '2.17']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ansible-core==${{ matrix.ansible-core }}.*
      - run: |
          for playbook in *.yml; do
            ansible-playbook --syntax-check -i inventories/localhost "$playbook"
          done
```

---

### Priority 5 — `role-structure-audit.yml`

Enforces AGENTS.md role structure conventions — every role must have required files.

```yaml
name: Role Structure Audit

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate role structure
        run: |
          failed=0
          for role in roles/*/; do
            role_name=$(basename "$role")
            for required in \
              "tasks/main.yml" \
              "defaults/main.yml" \
              "meta/main.yml" \
              "README.md"; do
              if [ ! -f "${role}${required}" ]; then
                echo "MISSING: ${role}${required}"
                failed=1
              fi
            done
          done
          exit $failed
```

---

### Priority 6 — `ee-validate.yml`

Cheaply validates Execution Environment definition changes on PRs without doing a full build.

```yaml
name: EE Validate

on:
  pull_request:
    paths:
      - 'execution-environment.yml'
      - 'requirements.yml'
      - 'bindep.txt'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ansible-builder==3.*
      - name: Validate EE definition (no build)
        run: ansible-builder create --verbosity 3
```

---

### Priority 7 — `release.yml`

Auto-generates GitHub Releases with release notes when a version tag is pushed.

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
```

---

## Priority Order

| Priority | Action | Impact |
|----------|--------|--------|
| 1 | **Delete** `molecule-actions.yml` | Removes always-failing dead workflow |
| 2 | **Add** `lint.yml` | Catches the most common contribution errors |
| 3 | **Fix** `validate.yml` (5 issues) | Makes existing syntax-check actually work correctly |
| 4 | **Add** `security-scan.yml` | Prevents credential leaks — high risk category |
| 5 | **Fix** `spotter-ci.yml` (4 issues) | Reduces noise, improves reliability |
| 6 | **Add** `syntax-check-matrix.yml` | Catches ansible-core compatibility issues |
| 7 | **Fix** `build-execution-environment.yml` (5 issues) | Stabilizes EE builds |
| 8 | **Add** `role-structure-audit.yml` | Enforces AGENTS.md conventions automatically |
| 9 | **Add** `ee-validate.yml` | Cheap PR feedback on EE definition changes |
| 10 | **Add** `release.yml` | Automates release management |

---

## Supporting Files Required

| File | Purpose |
|------|---------|
| `.yamllint` | yamllint configuration (line length, truthy values, etc.) |
| `.cspell.json` | cspell word list (add `dashlane`, `cloudability`, `viscosity`, etc.) |
| `requirements-dev.txt` | Pin `ansible-lint`, `ansible-builder`, etc. for reproducible CI |

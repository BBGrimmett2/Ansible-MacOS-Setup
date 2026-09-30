# Targeted Playbooks Architecture

## 1. Problem Statement

The main entry point, `playbooks/bootstrap_workstation.yml`, is designed for full workstation provisioning from scratch. It runs all 13 roles in a fixed sequence and has two characteristics that make it unsuitable for targeted, day-to-day config changes:

**Interactive prompts that cannot be skipped:**
- A `vars_prompt` at the top requires typing "personal" or "work" before any task runs — no `--extra-vars` shortcut suppresses the prompt display.
- `roles/development_tools/tasks/install_claude_code_work.yml` contains two `ansible.builtin.pause` tasks (VPN connect and VPN disconnect). These fire when `~/.config/claude-code-vertex/env.sh` does not exist. On a machine where Claude Code is already configured they are skipped — but on any other machine or after a config reset they block execution.

**Scope: everything runs, even unrelated roles:**
Running the full bootstrap to update a single git config value executes every role. Some of those roles trigger browser auth flows and VPN profile imports. There is no safe, documented shortcut without knowing internal tag structure.

**Tag structure is not self-documenting:**
The tags in `bootstrap_workstation.yml` (`foundation`, `system`, `tools`, `config`) group roles by category but do not map to user-facing concerns like "update git config" or "add an MCP server". Sub-task tags inside roles (e.g., `macos_defaults:dock`) are not visible to a user running `ansible-playbook --list-tags` against the bootstrap playbook.

---

## 2. Existing Targeted Playbooks

### What exists

| Playbook | Role(s) invoked | Interactive prompts | Notes |
|---|---|---|---|
| `playbooks/install_cli_tools.yml` | `cli_tools` | None | Safe to re-run |
| `playbooks/install_network_tools.yml` | `network_tools` | None | Safe to re-run |
| `playbooks/install_database_tools.yml` | `database_tools` | None | Safe to re-run |
| `playbooks/install_kubernetes_tools.yml` | `kubernetes_tools` | None | Safe to re-run |
| `playbooks/install_terminal.yml` | `terminal` | None | Safe to re-run |
| `playbooks/install_desktop_apps.yml` | `desktop_apps` | None | Safe to re-run |
| `playbooks/install_cloud_cli.yml` | `cloud_cli` | None | gcloud install is idempotent; auth not touched |
| `playbooks/configure_shell.yml` | `shell_environment` | None | Safe to re-run |
| `playbooks/verify_state.yml` | (inline tasks) | None | Read-only state snapshot |
| `playbooks/install_development_tools.yml` | `development_tools` | Conditional VPN pause (Claude Code work setup) | Too broad — runs everything in the role |
| `playbooks/setup_gcp_demo.yml` | `cloud_cli` | 4 prompts | Appropriately interactive for one-time demo setup |
| `playbooks/setup_aws_demo.yml` | `cloud_cli` | prompts | Same pattern |
| `playbooks/setup_azure_demo.yml` | `cloud_cli` | prompts | Same pattern |

### What is missing

| Concern | Existing task file | No targeted playbook |
|---|---|---|
| Git configuration | `roles/development_tools/tasks/configure_git.yml` | Only reachable via `install_development_tools.yml` (also runs Claude Code setup) |
| MCP server management | None | No role or task exists |
| Claude Code first-time setup | `install_claude_code_work.yml` | Embedded in broad role playbook with VPN pauses |
| Claude Code reconfiguration | None | No isolated path |
| SSH key refresh | `roles/ssh_config` (whole role) | No targeted playbook |
| macOS defaults subsections | `roles/macos_defaults/tasks/main.yml` (tagged) | Tags not exposed — user must know internal tag names |

---

## 3. Proposed Pattern

### 3.1 Naming convention

| Prefix | Meaning | Examples |
|---|---|---|
| `install_` | Idempotent tool/package installation | `install_cli_tools.yml`, `install_kubernetes_tools.yml` |
| `configure_` | Apply or refresh configuration (assumes tools installed) | `configure_git.yml`, `configure_ssh.yml`, `configure_mcp.yml` |
| `setup_` | One-time or interactive first-time setup | `setup_claude_code_work.yml`, `setup_gcp_demo.yml` |

### 3.2 Structure of a targeted playbook

```yaml
---
# =============================================================================
# <Human-readable purpose in one sentence>
# =============================================================================
# Purpose:  <what this does>
# Usage:    ansible-playbook playbooks/<name>.yml
# Requires: <prerequisites>
# Profile:  <personal | work | both>
# =============================================================================

- name: <Play name>
  hosts: localhost
  gather_facts: true

  vars:
    workstation_profile: "{{ workstation_profile | default('work') }}"

  roles:
    - role: <role_name>
      tags: [<role_name>]
```

**Structural rules:**

1. **No `vars_prompt` for `workstation_profile`** — use `default('work')`. Override via `-e workstation_profile=personal` when needed.
2. **No unconditional `ansible.builtin.pause`** — any pause must be guarded by a `stat` existence check. This pattern already exists in `install_claude_code_work.yml`; enforce it consistently.
3. **Declare prerequisites in the comment header**, not as mid-run failing tasks.
4. **One concern per playbook** — invoke one role, or a subset of tasks from one role via `tasks_from:`.
5. **Tags match the playbook name** — `configure_git.yml` carries tag `development_tools:git`.

### 3.3 Handling prerequisites

**Dashlane:** Include validation only (not a full secret fetch) via:
```yaml
  pre_tasks:
    - name: Validate Dashlane is available
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: validate
```

**VPN:** Never require VPN as a precondition in a `configure_` playbook. Tasks that require VPN must:
1. Check whether the target artifact already exists (`stat`).
2. Skip all VPN-gated steps if the artifact exists.
3. If VPN is genuinely required (first-time Vertex AI setup), use a `setup_` playbook with an explicit pause so the interactive nature is expected.

### 3.4 Tag strategy

Two-level scheme:
- Level 1 (`<role_name>`): selects the whole role.
- Level 2 (`<role_name>:<sub_concern>`): selects a specific task file. Already used in `macos_defaults` (`macos_defaults:dock`, `macos_defaults:finder`, etc.) — extend to `development_tools` and `shell_environment`.

```yaml
# In roles/development_tools/tasks/main.yml
- name: Configure git
  ansible.builtin.import_tasks: configure_git.yml
  tags: [development_tools, development_tools:git]

- name: Configure MCP servers
  ansible.builtin.include_tasks: configure_mcp.yml
  tags: [development_tools, development_tools:mcp]
```

---

## 4. Specific Recommendations

### 4.1 `playbooks/configure_git.yml` — HIGH PRIORITY

**Rationale:** Git config changes frequently. Logic exists in `roles/development_tools/tasks/configure_git.yml` and is idempotent. Reaching it today requires running `install_development_tools.yml`, which also triggers Claude Code setup with potential VPN pause.

**Implementation:** Import `development_tools` role with `tasks_from: configure_git`. Profile via `default('work')`. No Dashlane call unless `development_tools_gitconfig_from_dashlane: true`.

---

### 4.2 `playbooks/setup_claude_code_work.yml` — HIGH PRIORITY

**Rationale:** The VPN pause blocks in `install_claude_code_work.yml` should live in a `setup_` playbook that is explicitly first-time/interactive — not embedded inside `install_development_tools.yml`. Once `~/.config/claude-code-vertex/env.sh` exists, this playbook becomes a no-op.

**Side effect:** `install_development_tools.yml` can set `development_tools_claude_code_enabled: false` in its `vars:` block, making the broad role playbook non-interactive.

---

### 4.3 `playbooks/configure_claude_code.yml` — HIGH PRIORITY

**Rationale:** After initial setup, users need to reconfigure (update Vertex AI token, swap GCP project). Should not require VPN if `env.sh` already exists.

**Implementation:**
1. Assert `~/.config/claude-code-vertex/env.sh` exists (fail with message to run `setup_claude_code_work.yml` first).
2. Fetch updated GCP project ID from Dashlane.
3. Update `env.sh` in-place.

No `pause` tasks.

---

### 4.4 `playbooks/configure_mcp.yml` — HIGH PRIORITY

**Rationale:** MCP server management is an explicit target use case. The tasks now exist in `roles/development_tools/tasks/configure_mcp.yml` but are only reachable via the broad `install_development_tools.yml`.

**Implementation:** Thin playbook importing `development_tools` with `tasks_from: configure_mcp`. No VPN, no installation steps.

```bash
ansible-playbook playbooks/configure_mcp.yml
```

---

### 4.5 `playbooks/configure_ssh.yml` — MEDIUM PRIORITY

**Rationale:** The `ssh_config` role is idempotent. A user adding a new SSH key to Dashlane must currently run the full bootstrap to deploy it.

**Implementation:** Single-role targeted playbook with Dashlane validation pre_task.

```bash
ansible-playbook playbooks/configure_ssh.yml
ansible-playbook playbooks/configure_ssh.yml -e workstation_profile=personal
```

---

### 4.6 `playbooks/configure_macos.yml` — MEDIUM PRIORITY

**Rationale:** The `macos_defaults` role already has sub-task tags. A dedicated playbook exposes them without requiring knowledge of bootstrap internals.

```bash
ansible-playbook playbooks/configure_macos.yml                        # all defaults
ansible-playbook playbooks/configure_macos.yml --tags macos_defaults:dock
```

---

### 4.7 `playbooks/deploy_certificates.yml` — MEDIUM PRIORITY

**Rationale:** Deploying a corporate CA certificate to the system trust store is an isolated, common operation. No role or playbook covers this.

**Implementation:** Wrap `roles/network_tools/tasks/deploy_certificates.yml` with Dashlane validation.

---

### 4.8 `playbooks/refresh_secrets.yml` — LOW PRIORITY

**Rationale:** SSH keys and Dashlane-backed gitconfig need refreshing when credentials rotate. Currently requires full bootstrap.

**Implementation:** Chain SSH and git configure tasks under a single Dashlane validation pre_task.

---

## 5. Usage Examples

```bash
# Update git config
ansible-playbook playbooks/configure_git.yml

# Add/update MCP servers
ansible-playbook playbooks/configure_mcp.yml

# First-time Claude Code setup (work, requires VPN)
ansible-playbook playbooks/setup_claude_code_work.yml

# Reconfigure Claude Code (no VPN needed)
ansible-playbook playbooks/configure_claude_code.yml

# Refresh SSH keys from Dashlane
ansible-playbook playbooks/configure_ssh.yml

# Apply Dock settings only
ansible-playbook playbooks/configure_macos.yml --tags macos_defaults:dock

# Personal profile git config
ansible-playbook playbooks/configure_git.yml -e workstation_profile=personal

# Full bootstrap (new machine only)
ansible-playbook playbooks/bootstrap_workstation.yml
```

---

## Implementation Order

1. `configure_git.yml` — no new roles, just a thin playbook
2. `configure_ssh.yml` — same pattern
3. `configure_mcp.yml` — wraps new `configure_mcp.yml` tasks already created
4. `setup_claude_code_work.yml` — extracts VPN pauses from `install_development_tools.yml`
5. `configure_claude_code.yml` — new reconfiguration tasks
6. `configure_macos.yml` — expose existing tags
7. `deploy_certificates.yml` — wrap existing network_tools task
8. `refresh_secrets.yml` — chain existing tasks

**Do not split roles.** Targeted playbooks call existing roles via `tasks_from:`. Role boundaries reflect installation domains; targeted playbooks handle operational use cases.

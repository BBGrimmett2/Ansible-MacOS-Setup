# macOS Workstation Ansible - Testing Strategy

**Generated:** 2026-09-29
**Purpose:** Comprehensive testing approach for safe, incremental testing on actual hardware

---

## Overview

This document outlines the complete testing strategy for the macOS Ansible automation project. The approach is designed to:

1. **Test incrementally** as roles are built (not all at once)
2. **Test safely** on production laptop without breaking it
3. **Validate thoroughly** before wipe-and-repeat testing
4. **Enable confidence** that automation works correctly

---

## 1. Incremental Testing Workflow (Test as You Build)

### Testing Philosophy

**Layered Testing Approach:**
1. **Syntax Validation** - Catch errors before execution
2. **Check Mode** - Dry-run to see planned changes
3. **Limited Scope Tests** - Test one role at a time
4. **Idempotency Tests** - Verify no changes on second run
5. **Integration Tests** - Test role interactions
6. **Full System Tests** - Complete end-to-end validation

### Pre-Execution Testing (No System Changes)

These tests are **completely safe** and should be run before every actual execution:

#### A. Syntax Validation

```bash
# Check playbook syntax (catches YAML and Ansible syntax errors)
ansible-playbook --syntax-check playbooks/test_homebrew.yml

# Check all playbooks at once
for playbook in playbooks/*.yml; do
  echo "Checking $playbook"
  ansible-playbook --syntax-check "$playbook"
done
```

#### B. Linting (Code Quality)

```bash
# Ansible lint - checks best practices
ansible-lint roles/homebrew/

# YAML lint - checks YAML formatting
yamllint roles/homebrew/

# Run both on all content
ansible-lint
yamllint .
```

#### C. Check Mode (Dry Run)

```bash
# See what WOULD change without making changes
ansible-playbook playbooks/test_homebrew.yml --check

# Check mode with diff (show file changes)
ansible-playbook playbooks/test_homebrew.yml --check --diff

# Verbose check mode to understand logic flow
ansible-playbook playbooks/test_homebrew.yml --check --diff -v
```

**Safety Note:** Check mode has limitations:
- Some modules don't support check mode (will be skipped)
- Modules that gather info (stat, command with changed_when: false) run normally
- Dependent tasks may fail if earlier tasks were skipped
- Still useful for catching ~80% of issues safely

---

## 2. Test Playbook Templates

### Role Test Playbook Template

Each role should have a dedicated test playbook in `playbooks/tests/`:

**Example: `playbooks/tests/test_homebrew.yml`**

```yaml
---
# =============================================================================
# Test Playbook: Homebrew Role
# =============================================================================
# Purpose: Test homebrew role installation and configuration in isolation
# Usage:
#   Dry run: ansible-playbook playbooks/tests/test_homebrew.yml --check
#   Execute: ansible-playbook playbooks/tests/test_homebrew.yml
#   Verify:  ansible-playbook playbooks/tests/test_homebrew.yml (should show no changes)
# =============================================================================

- name: Test Homebrew Role
  hosts: localhost
  gather_facts: true

  vars:
    # Test-specific overrides (if needed)
    homebrew_update: false  # Skip update for faster testing
    homebrew_upgrade_all: false

  tasks:
    - name: Display test information
      ansible.builtin.debug:
        msg:
          - "=== Homebrew Role Test ==="
          - "Mode: {{ 'CHECK MODE (dry run)' if ansible_check_mode else 'EXECUTION MODE' }}"
          - "User: {{ ansible_env.USER }}"
          - "Architecture: {{ ansible_architecture }}"

    - name: Execute homebrew role
      ansible.builtin.import_role:
        name: homebrew
      tags: homebrew

    - name: Verify homebrew installation
      block:
        - name: Check brew command exists
          ansible.builtin.command: which brew
          register: brew_which
          changed_when: false
          failed_when: brew_which.rc != 0

        - name: Get Homebrew version
          ansible.builtin.command: brew --version
          register: brew_version
          changed_when: false

        - name: Display verification results
          ansible.builtin.debug:
            msg:
              - "✓ Homebrew installed successfully"
              - "Location: {{ brew_which.stdout }}"
              - "Version: {{ brew_version.stdout_lines[0] }}"
      tags: verify
```

### Progressive Test Playbooks by Phase

**Phase 2: Foundation Components**
- `playbooks/tests/test_homebrew.yml`
- `playbooks/tests/test_dashlane_secrets.yml`
- `playbooks/tests/test_foundation.yml` - Combined test

**Phase 3: System Configuration**
- `playbooks/tests/test_macos_defaults.yml`
- `playbooks/tests/test_pam_security.yml`
- `playbooks/tests/test_ssh_config.yml`
- `playbooks/tests/test_system_config.yml` - Combined

**Phase 4: Shell and CLI Tools**
- `playbooks/tests/test_shell_environment.yml`
- `playbooks/tests/test_cli_tools.yml`
- `playbooks/tests/test_terminal.yml`

---

## 3. Checkpoint System (Test Piece by Piece)

### Tag-Based Checkpoint Strategy

Add granular tags to enable selective execution:

**Tag Hierarchy:**

```yaml
# In role tasks/main.yml
- name: Install package
  community.general.homebrew:
    name: jq
  tags:
    - cli_tools          # Role level
    - cli_tools:install  # Function level
    - cli_tools:jq       # Package level
```

**Checkpoint Commands:**

```bash
# Test only validation
ansible-playbook playbooks/test_cli_tools.yml --tags validate

# Test only installation, skip configuration
ansible-playbook playbooks/test_cli_tools.yml --tags install

# Test specific package
ansible-playbook playbooks/test_cli_tools.yml --tags cli_tools:jq

# Skip expensive operations
ansible-playbook playbooks/test_all.yml --skip-tags "update,upgrade"
```

---

## 4. Safe Testing on Production Workstation

### Safety Measures

#### A. Pre-Flight Safety Checks

Create `playbooks/tasks/preflight_safety.yml`:

```yaml
---
# Preflight safety checks before making system changes

- name: Verify not running as root
  ansible.builtin.assert:
    that:
      - ansible_env.USER != 'root'
    fail_msg: "Do not run as root! Run as your normal user account."

- name: Verify macOS version
  ansible.builtin.assert:
    that:
      - ansible_distribution == 'MacOSX'
      - ansible_distribution_version is version('12.0', '>=')
    fail_msg: "Unsupported macOS version"

- name: Check disk space
  ansible.builtin.shell: df -h / | awk 'NR==2 {print $4}'
  register: disk_space
  changed_when: false

- name: Verify backup exists
  ansible.builtin.pause:
    prompt: |
      ⚠️  SAFETY CHECK ⚠️

      Before proceeding, verify you have:
      1. Time Machine backup OR
      2. Manual backup of critical files

      Type 'yes' to confirm
  register: backup_confirm
  when: not ansible_check_mode
```

#### B. State Capture (Before Testing)

Capture current system state for comparison and rollback:

```bash
# Create state directory
mkdir -p .test_state

# Capture installed packages
brew list --formula > .test_state/brew_formula_before.txt
brew list --cask > .test_state/brew_cask_before.txt

# Capture shell config
cp ~/.zshrc .test_state/zshrc_before
cp ~/.ssh/config .test_state/ssh_config_before

# Save timestamp
date > .test_state/capture_timestamp.txt
```

---

## 5. Full End-to-End Testing Plan

### Master Test Playbook

Create `playbooks/tests/test_workstation_full.yml`:

```yaml
---
- name: Full Workstation Setup Test
  hosts: localhost
  gather_facts: true

  vars_prompt:
    - name: workstation_profile
      prompt: "Select profile (personal/work)"
      private: false
      default: "personal"

    - name: confirm_execution
      prompt: |
        ⚠️  This will make system changes!
        Profile: {{ workstation_profile }}
        Mode: {{ 'DRY RUN' if ansible_check_mode else 'EXECUTION' }}
        Continue? (yes/no)
      private: false
      default: "no"

  pre_tasks:
    - name: Verify user confirmation
      ansible.builtin.assert:
        that: confirm_execution | lower == 'yes'
        fail_msg: "Test cancelled by user"

  roles:
    # Phase 1: Foundation
    - role: homebrew
      tags: [foundation, homebrew]

    - role: dashlane_secrets
      tags: [foundation, dashlane]

    # Phase 2: System Configuration
    - role: macos_defaults
      tags: [system, macos]

    - role: pam_security
      tags: [system, security]

    - role: ssh_config
      tags: [system, ssh]

    # Phase 3: Shell & CLI
    - role: shell_environment
      tags: [shell]

    - role: cli_tools
      tags: [tools, cli]
```

---

## 6. Wipe-and-Repeat Test Strategy

### Full System Test Protocol

**Phase 1: Pre-Wipe Preparation**

```bash
# 1. Run state capture
ansible-playbook playbooks/tests/capture_system_state.yml

# 2. Export Homebrew packages
brew bundle dump --file=Brewfile.backup

# 3. Backup critical configs not managed by Ansible
tar -czf ~/backup_manual_configs.tar.gz \
  ~/.aws \
  ~/.config/[custom_apps] \
  ~/Documents/important

# 4. Verify Dashlane master password is available
```

**Phase 2: Fresh macOS Setup**

1. Create bootable USB installer (if needed)
2. Boot from Recovery Mode (hold Cmd+R)
3. Erase disk and reinstall macOS
4. Complete minimal Apple Setup

**Phase 3: Web Installer Test**

```bash
# One-line installation (recommended)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh)" \
  2>&1 | tee ~/install_test_log.txt

# The installer automatically:
# - Installs all prerequisites
# - Clones repository
# - Authenticates Dashlane (prompts for credentials)
# - Runs bootstrap_workstation.yml playbook
```

**Phase 4: Additional Testing**

After installation completes:

```bash
# Activate virtual environment
source ~/venv-ansible/bin/activate
cd ~/ansible-macos-setup

# Test specific categories
ansible-playbook playbooks/install_cli_tools.yml --check
ansible-playbook playbooks/install_cloud_cli.yml --check

# Test demo environment setup
ansible-playbook playbooks/setup_aws_demo.yml
```

**Phase 5: Idempotency Test**

```bash
# Run again - should show no changes
ansible-playbook playbooks/tests/test_workstation_full.yml \
  -e "workstation_profile=personal" \
  2>&1 | tee ~/test_idempotency.log

# Check for any "changed" tasks
grep -i "changed=" ~/test_idempotency.log
```

---

## 7. Validation Checklist for Each Role

### Role Testing Checklist Template

```markdown
# Role Testing Checklist: [ROLE_NAME]

## Pre-Testing
- [ ] Syntax check passes
- [ ] Ansible-lint passes
- [ ] YAML lint passes
- [ ] Check mode runs without errors

## Installation Testing
- [ ] Fresh install succeeds
- [ ] Installed component is functional
- [ ] Configuration files created with correct permissions
- [ ] No errors in Ansible output

## Idempotency Testing
- [ ] Second run shows "ok" (no changes)
- [ ] Third run shows "ok" (no changes)
- [ ] `changed` count is 0 on subsequent runs

## Removal Testing
- [ ] Uninstall succeeds (state: absent)
- [ ] All files removed
- [ ] Configuration cleaned up
```

---

## 8. Testing Workflow Summary

### Daily Development Testing (As You Build)

```bash
# 1. After writing a role
ansible-playbook --syntax-check playbooks/tests/test_[role].yml
ansible-lint roles/[role]/
yamllint roles/[role]/

# 2. Test in check mode
ansible-playbook playbooks/tests/test_[role].yml --check --diff

# 3. Test actual execution
ansible-playbook playbooks/tests/test_[role].yml

# 4. Test idempotency
ansible-playbook playbooks/tests/test_[role].yml
# Should show 0 changed

# 5. Git commit
git add roles/[role]/
git commit -m "Add [role] with tests"
```

### Weekly Integration Testing

```bash
# Test multiple roles together
ansible-playbook playbooks/tests/test_foundation.yml      # Phase 1
ansible-playbook playbooks/tests/test_system_config.yml   # Phase 2

# Full integration test
ansible-playbook playbooks/tests/test_workstation_full.yml --check
ansible-playbook playbooks/tests/test_workstation_full.yml
```

---

## 9. Rollback and Cleanup Strategies

### Automated Rollback

Each role should support `state: absent` for clean removal.

**Example cleanup playbook:**

```yaml
# playbooks/cleanup/remove_cli_tools.yml
---
- name: Remove CLI Tools
  hosts: localhost

  tasks:
    - name: Remove CLI tools
      ansible.builtin.import_role:
        name: cli_tools
      vars:
        cli_tools_state: absent
```

### Manual Cleanup Checklist

After each test session:

- [ ] Review installed packages: `brew list`
- [ ] Check modified config files: `git status ~`
- [ ] Remove test SSH keys: `ls -la ~/.ssh/`
- [ ] Clear Ansible facts cache: `rm -rf /tmp/ansible_facts_cache`

---

## 10. Testing Helper Script

Create `scripts/test_helper.sh`:

```bash
#!/bin/bash
# Helper script for common testing tasks

function syntax_check_all() {
    for playbook in playbooks/*.yml playbooks/tests/*.yml; do
        [ -f "$playbook" ] || continue
        echo "Checking: $playbook"
        ansible-playbook --syntax-check "$playbook"
    done
}

function lint_all() {
    ansible-lint
    yamllint .
}

function test_role() {
    local role_name="$1"
    ansible-playbook --syntax-check "playbooks/tests/test_$role_name.yml"
    ansible-playbook "playbooks/tests/test_$role_name.yml" --check --diff
    ansible-playbook "playbooks/tests/test_$role_name.yml"
    ansible-playbook "playbooks/tests/test_$role_name.yml"  # Idempotency
}

case "${1:-help}" in
    syntax) syntax_check_all ;;
    lint) lint_all ;;
    test-role) test_role "$2" ;;
    *) echo "Usage: $0 {syntax|lint|test-role <name>}" ;;
esac
```

Usage:

```bash
./scripts/test_helper.sh syntax              # Check all syntax
./scripts/test_helper.sh lint                # Run all linters
./scripts/test_helper.sh test-role homebrew  # Full test of one role
```

---

## Next Steps for Testing Implementation

### Immediate Actions

1. Create test playbooks for completed roles:
   - `playbooks/tests/test_homebrew.yml`
   - `playbooks/tests/test_dashlane_secrets.yml`
   - `playbooks/tests/test_macos_defaults.yml`
   - `playbooks/tests/test_pam_security.yml`
   - `playbooks/tests/test_ssh_config.yml`

2. Create testing helper script:
   - `scripts/test_helper.sh`

3. Test on your laptop:
   - Start with check mode only
   - Test one role at a time
   - Verify idempotency

### Before Wipe Testing

1. Complete all roles
2. Create full test playbook
3. Test on current system
4. Fix all issues
5. Document known issues
6. **Then** do wipe-and-repeat test

---

## Safety Reminders

⚠️ **Always:**
- Run check mode first
- Test one role at a time
- Have backups before testing
- Document issues immediately
- Test idempotency

⚠️ **Never:**
- Test as root user
- Skip validation checks
- Test multiple changes at once
- Assume it works without testing

---

For questions or issues, refer to:
- AGENTS.md - Development standards
- README.md - Project overview
- docs/planning/repository_cleanup_todo.md - Known issues

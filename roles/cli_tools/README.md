# CLI Tools Role

Install and configure essential command-line quality-of-life tools for macOS.

## Overview

This role manages installation and configuration of modern CLI tools that enhance productivity:

- **jq** - JSON processor
- **yq** - YAML processor
- **direnv** - Per-directory environment variables
- **eza** - Modern ls replacement
- **bat** - Modern cat replacement with syntax highlighting
- **fd** - Modern find replacement
- **fzf** - Fuzzy finder
- **git-delta** - Git diff pager with syntax highlighting

## Special Feature: direnv Safety Checks

When enabled, direnv is configured with interactive safety prompts when entering directories under `~/Documents/Projects/`. This prevents accidentally loading environment variables from the wrong project, which is especially useful when working with multiple demo or test environments that use similar credentials.

**How it works:**
- Custom `~/.config/direnv/direnvrc` with `use_project_env` function
- Prompts for confirmation before loading `.envrc` in Projects/ subdirectories
- Shows current directory and project name
- User must type 'y' or 'Y' to confirm environment loading

**Example `.envrc` usage:**
```bash
# ~/Documents/Projects/demo-aws-project/.envrc
use_project_env
export AWS_PROFILE=demo-aws
export ENV=staging
```

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

### Installation Control

```yaml
# Install or remove CLI tools
cli_tools_state: present  # or 'absent'

# Install all tools (if false, only install enabled tools)
cli_tools_install_all: true
```

### Individual Tool Control

```yaml
cli_tools_jq_enabled: true
cli_tools_yq_enabled: true
cli_tools_direnv_enabled: true
cli_tools_eza_enabled: true
cli_tools_bat_enabled: true
cli_tools_fd_enabled: true
cli_tools_fzf_enabled: true
cli_tools_git_delta_enabled: true
```

### direnv Configuration

```yaml
# Configure direnv with custom direnvrc
cli_tools_direnv_configure: true

# Enable safety prompts in Projects/ directory
cli_tools_direnv_safety_enabled: true

# Projects directory path for safety checks
cli_tools_direnv_projects_path: "{{ ansible_env.HOME }}/Documents/Projects"

# direnv configuration directory
cli_tools_direnv_config_dir: "{{ ansible_env.HOME }}/.config/direnv"

# direnv configuration file
cli_tools_direnv_config_file: "{{ cli_tools_direnv_config_dir }}/direnvrc"
```

### Tool-Specific Configuration

```yaml
# bat theme (syntax highlighting)
cli_tools_bat_theme: "TwoDark"

# fd - respect .gitignore by default
cli_tools_fd_respect_gitignore: true

# fzf - default options
cli_tools_fzf_default_opts: "--height 40% --layout=reverse --border"

# git-delta - side-by-side diffs
cli_tools_git_delta_side_by_side: true
```

## Dependencies

- `homebrew` role

## Public Functions (tasks_from)

All public functions can be called independently using `tasks_from`:

### Installation Functions

```yaml
# Install individual tools
- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_jq

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_yq

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_direnv

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_eza

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_bat

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_fd

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_fzf

- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: install_git_delta
```

### Configuration Functions

```yaml
# Configure direnv with safety checks
- ansible.builtin.import_role:
    name: cli_tools
    tasks_from: configure_direnv
```

## Example Playbook

### Install All Tools

```yaml
---
- name: Install CLI tools
  hosts: localhost
  roles:
    - role: cli_tools
```

### Install Specific Tools Only

```yaml
---
- name: Install selected CLI tools
  hosts: localhost
  roles:
    - role: cli_tools
      vars:
        cli_tools_install_all: false
        cli_tools_jq_enabled: true
        cli_tools_yq_enabled: true
        cli_tools_direnv_enabled: true
        cli_tools_eza_enabled: false
        cli_tools_bat_enabled: false
        cli_tools_fd_enabled: false
        cli_tools_fzf_enabled: false
        cli_tools_git_delta_enabled: false
```

### Configure direnv Without Safety Checks

```yaml
---
- name: Configure direnv (no safety prompts)
  hosts: localhost
  roles:
    - role: cli_tools
      vars:
        cli_tools_direnv_safety_enabled: false
```

### Remove All Tools

```yaml
---
- name: Remove CLI tools
  hosts: localhost
  roles:
    - role: cli_tools
      vars:
        cli_tools_state: absent
```

## Tags

- `validate` - Run validation tasks only
- `install` - Run installation tasks only
- `configure` - Run configuration tasks only

**Usage:**
```bash
# Install only
ansible-playbook playbooks/install_cli_tools.yml --tags install

# Configure only
ansible-playbook playbooks/install_cli_tools.yml --tags configure

# Skip validation
ansible-playbook playbooks/install_cli_tools.yml --skip-tags validate
```

## Testing

### Syntax Check

```bash
ansible-playbook --syntax-check playbooks/tests/test_cli_tools.yml
```

### Dry Run

```bash
ansible-playbook --check playbooks/tests/test_cli_tools.yml
```

### Execute

```bash
ansible-playbook playbooks/tests/test_cli_tools.yml
```

### Verify Idempotency

```bash
# Run twice - second run should show no changes
ansible-playbook playbooks/tests/test_cli_tools.yml
ansible-playbook playbooks/tests/test_cli_tools.yml
```

## direnv Safety Check Demo

After installing with safety checks enabled:

```bash
# Create a test project
mkdir -p ~/Documents/Projects/test-project
cd ~/Documents/Projects/test-project

# Create .envrc
cat > .envrc << 'EOF'
use_project_env
export TEST_VAR=value
EOF

# Allow direnv
direnv allow

# cd into directory - you'll see:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚠️  direnv: Project environment detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Current directory: /Users/you/Projects/test-project
# Project: test-project
#
# Are you in the correct project? (y/N):

# Type 'y' to load environment, 'n' or anything else to skip
```

## License

MIT

## Author

Brian Grimmett

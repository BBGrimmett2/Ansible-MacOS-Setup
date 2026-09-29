---
# Development Tools Role

Install and configure development and automation tools with profile-specific settings.

## Overview

This role manages:

- **pre-commit** - Git hooks framework for code quality
- **Git configuration** - Profile-specific user settings
- **Custom shell scripts** - rhdps and extensible framework
- **Claude Code CLI** - AI coding assistant (work profile)
- **AAP demo tools** - Ansible Automation Platform tools (work profile)

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)
- Git (built-in on macOS)

## Role Variables

### Basic Configuration

```yaml
# Install or remove development tools
development_tools_state: present

# Configure git globally
development_tools_configure_git: true

# Enable pre-commit
development_tools_precommit_enabled: true

# Enable custom scripts
development_tools_custom_scripts_enabled: true
```

### Git Configuration

```yaml
# Personal profile
git_user_name_personal: "Your Name"
git_user_email_personal: "you@personal.com"

# Work profile
git_user_name_work: "Your Name"
git_user_email_work: "you@company.com"

# Git settings
development_tools_git_default_branch: main
development_tools_git_editor: vim
```

### Work Profile Tools

```yaml
# Claude Code CLI (work only)
development_tools_claude_code_enabled: true  # auto-enabled for work profile

# AAP demo tools (work only)
development_tools_aap_demo_enabled: true  # auto-enabled for work profile
```

## Dependencies

- `homebrew` role

## Example Playbook

```yaml
---
- name: Install development tools
  hosts: localhost
  roles:
    - role: development_tools
```

## Features

### pre-commit

Installed globally for all git repositories:

```bash
# In any git repository
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Git Configuration

Automatically configured based on profile:

**Personal profile:**
```
git config --global user.name "Your Name"
git config --global user.email "you@personal.com"
```

**Work profile:**
```
git config --global user.name "Your Name"
git config --global user.email "you@company.com"
```

### Custom Scripts

Includes **rhdps** command for cloud demo setup:

```bash
# Setup AWS demo environment
rhdps setup aws

# Setup GCP demo environment
rhdps setup gcp

# Setup Azure demo environment
rhdps setup azure
```

See `custom_scripts/README.md` for extensibility.

### Claude Code CLI (Work Profile)

```bash
# TODO: Installation instructions
# Manual: npm install -g @anthropic-ai/claude-code
```

### AAP Demo Tools (Work Profile)

```bash
# TODO: Installation instructions
# ansible-navigator
# ansible-builder
```

## Post-Installation

### Verify Git Configuration

```bash
git config --global --list
```

### Test pre-commit

```bash
cd /path/to/git/repo
pre-commit install
pre-commit run --all-files
```

### Test Custom Scripts

```bash
rhdps help
```

## Profile-Specific Behavior

**Personal Profile:**
- Personal git credentials
- pre-commit
- Custom scripts
- No Claude Code
- No AAP tools

**Work Profile:**
- Work git credentials (Red Hat email)
- pre-commit with ansible-lint
- Custom scripts (including rhdps)
- Claude Code CLI
- AAP demo tools

## License

MIT

## Author

Brian Grimmett

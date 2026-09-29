# Shell Environment Role

Configure ZSH shell environment with modern tool integrations and productivity enhancements.

## Overview

This role deploys a comprehensive ZSH configuration that integrates all installed CLI tools:

- **Modern aliases** for eza, bat, kubectl, git
- **Tool integrations** for direnv, fzf, completions
- **Custom prompt** with git branch and kubectl context
- **Productivity functions** for common tasks
- **Profile awareness** for personal/work configurations

## Requirements

- macOS with ZSH (built-in on modern macOS)
- cli_tools role (for eza, bat, fzf, direnv)
- terminal role (for Nerd Fonts in prompt)

## Role Variables

### Basic Configuration

```yaml
# Configure or restore defaults
shell_environment_state: present

# Backup existing .zshrc
shell_environment_backup_existing: true

# Enable modern tool aliases
shell_environment_modern_aliases: true

# Custom prompt
shell_environment_custom_prompt: true
shell_environment_prompt_style: detailed  # or 'simple'
```

### Tool Integrations

```yaml
# direnv integration
shell_environment_direnv_enabled: true

# fzf key bindings
shell_environment_fzf_enabled: true

# Completion systems
shell_environment_kubectl_completion: true
shell_environment_helm_completion: true
shell_environment_gh_completion: true
```

### Environment Variables

```yaml
# Default editor
shell_environment_editor: vim

# Language/locale
shell_environment_lang: en_US.UTF-8

# Custom variables
shell_environment_extra_vars:
  MY_VAR: value
```

## Dependencies

- `homebrew` role
- `cli_tools` role
- `terminal` role

## Example Playbook

```yaml
---
- name: Configure shell environment
  hosts: localhost
  roles:
    - role: shell_environment
```

## Features

### Modern Aliases

```bash
# File operations (using eza)
ls      # eza --icons --git
ll      # eza --icons --git -lh
la      # eza --icons --git -lha
tree    # eza --tree --icons

# Cat replacement (using bat)
cat     # bat --paging=never

# Kubernetes shortcuts
k       # kubectl
kgp     # kubectl get pods
kgs     # kubectl get svc
kctx    # kubectx
kns     # kubens

# Git shortcuts
g       # git
gs      # git status
ga      # git add
gc      # git commit
gp      # git push
gl      # git log --oneline --graph

# Directory navigation
..      # cd ..
...     # cd ../..
....    # cd ../../..
```

### Custom Functions

```bash
# Create and enter directory
mkcd my-project

# Extract any archive
extract file.tar.gz

# Kill process on port
killport 3000
```

### Prompt Features

**Detailed prompt shows:**
- Current directory (with colors)
- Git branch with status (green = clean, yellow = changes)
- Kubernetes context and namespace
- Timestamp on right side

Example:
```
~/Projects/my-app git:(main*) k8s:(dev/default)
❯
```

### Tool Integration

**direnv** - Automatic environment loading:
```bash
cd ~/Projects/demo-aws
# Automatically loads .envrc with AWS credentials
```

**fzf** - Fuzzy finding:
```bash
# Ctrl+R: Search command history
# Ctrl+T: Search files
# Alt+C: Search directories
```

**Completions:**
- kubectl commands and resources
- helm commands
- GitHub CLI commands

## Post-Installation

### Reload Configuration

```bash
# Reload in current session
source ~/.zshrc

# Or open new terminal
```

### Verify Installation

```bash
# Check aliases
alias ls
# Should show: eza --icons --git

# Check git prompt
cd /path/to/git/repo
# Should show branch in prompt

# Test fzf
# Press Ctrl+R to search history
```

### Customization

Add personal customizations to `~/.zshrc.local`:

```bash
# This file is sourced at the end of .zshrc
# Add your custom aliases, functions, or overrides here

alias myalias='custom command'
export MY_VAR=value
```

The `.zshrc.local` file is never overwritten by Ansible.

## Profile-Specific Configuration

**Work profile includes:**
- `WORK_MODE=true` environment variable
- Can add work-specific aliases/functions

## Backup and Restore

### Backups

Existing `.zshrc` is backed up to:
```
~/.zshrc.backup.<timestamp>
```

### Restore

To restore original configuration:
```bash
# Find your backup
ls -la ~/.zshrc.backup.*

# Restore it
cp ~/.zshrc.backup.XXXXXXXXXX ~/.zshrc
source ~/.zshrc
```

## Troubleshooting

### Prompt not showing colors

Check terminal supports 256 colors:
```bash
echo $TERM
# Should be: xterm-256color or similar
```

### kubectl completion not working

Ensure kubectl is installed:
```bash
which kubectl
```

### fzf key bindings not working

Check fzf is installed:
```bash
which fzf
```

## License

MIT

## Author

Brian Grimmett

# macOS Workstation Automation

Comprehensive Ansible automation for macOS workstation setup and configuration. Supports both personal and work (Red Hat) environments with profile-based configuration, secure secret management via Dashlane CLI, and special tooling for cloud demo environments.

**Status:** In Active Development

---

## Features

- **Zero-to-Hero Bootstrap** - Single script to go from fresh Mac to Ansible-ready
- **Secure Secret Management** - No hardcoded credentials; all secrets via Dashlane CLI
- **Profile-Aware** - Interactive personal/work profile selection with separate configurations
- **Cloud Demo Helpers** - Quick setup for AWS/Azure/GCP demo environments
- **direnv Safety** - Confirmation prompts for Projects/ directory environment loading
- **Category-Based Roles** - Logical tool grouping (not monolithic, not per-tool explosion)
- **Idempotent** - Safe to run multiple times; only changes what's needed
- **AGENTS.md Compliant** - Follows Red Hat CoP best practices

---

## Quick Start

### One-Line Installation (Recommended)

Run this command on a fresh macOS machine to install everything:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh)"
```

This will:
1. Install Xcode Command Line Tools
2. Install Homebrew
3. Install Python and Ansible
4. Install Dashlane CLI
5. Clone this repository
6. Run the bootstrap playbook (prompts for profile selection)

**Alternative shorter version:**
```bash
curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh | bash
```

### Manual Installation (From Cloned Repository)

If you prefer to clone first:

```bash
# Clone the repository
git clone https://github.com/BBGrimmett2/Ansible-MacOS-Setup.git
cd Ansible-MacOS-Setup

# Run the installer
./scripts/install.sh
```

---

## What Gets Installed

### Foundation (Always)
- Homebrew package manager
- Python 3 + Ansible virtual environment
- Dashlane CLI for secret management

### System Configuration
- macOS defaults (Dock, Finder, keyboard, trackpad)
- Touch ID for sudo authentication
- YubiKey support (pam_u2f)
- SSH configuration and keys (profile-specific)

### CLI Tools
- jq, yq (JSON/YAML parsing)
- eza, bat, fd (modern replacements for ls, cat, find)
- fzf (fuzzy finder)
- direnv (per-directory environments with safety checks)
- git-delta (enhanced git diffs)

### Terminal
- iTerm2 or Ghostty
- NerdFonts for icons

### Cloud CLIs
- AWS CLI
- Google Cloud CLI
- Azure CLI
- GitHub CLI (gh)

### Kubernetes Tools
- oc (OpenShift CLI)
- kubectl
- helm
- k9s (terminal UI)
- kubectx/kubens
- stern (multi-pod logs)

### Network Tools
- OpenVPN client
- bind tools (dig, nslookup)
- Bruno (API testing)
- VPN profiles (work profile only: Shadowman, root CAs)

### Database & Container Tools
- PGAdmin
- Podman Desktop

### Desktop Applications
- Google Chrome (set as default browser)
- VS Code (set as default editor)
- Cursor
- Google Drive
- Rectangle (window management)
- DisplayLink Manager
- Elgato Camera Hub & Control Center
- Obsidian
- Discord

### Development Tools (General)
- pre-commit framework
- Git global configuration (profile-specific)

### Development Tools (Work Profile Only)
- Claude Code CLI (Red Hat organization config)
- AAP-demo environment tools

---

## Project Structure

```
.
├── scripts/                 # Bootstrap scripts
│   └── bootstrap.sh         # Zero-to-Ansible setup
├── inventories/             # Inventory definitions
│   └── localhost.yml        # Local macOS inventory
├── group_vars/              # Global variables
│   └── all.yml              # Shared configuration
├── roles/                   # Ansible roles (category-based)
│   ├── homebrew/            # Homebrew package manager
│   ├── dashlane_secrets/    # Secret management
│   ├── macos_defaults/      # System preferences
│   ├── pam_security/        # Touch ID, YubiKey
│   ├── ssh_config/          # SSH setup
│   ├── shell_environment/   # ZSH, dotfiles, aliases
│   ├── cli_tools/           # CLI utilities
│   ├── terminal/            # Terminal emulator
│   ├── cloud_cli/           # Cloud provider CLIs
│   ├── kubernetes_tools/    # K8s/OpenShift tools
│   ├── network_tools/       # Network & VPN
│   ├── database_tools/      # Database tools
│   ├── desktop_apps/        # Desktop applications
│   └── development_tools/   # Dev tools & config
├── playbooks/               # Ansible playbooks
│   ├── bootstrap_workstation.yml  # Master playbook
│   ├── setup_aws_demo.yml         # AWS demo env setup
│   ├── setup_gcp_demo.yml         # GCP demo env setup
│   ├── setup_azure_demo.yml       # Azure demo env setup
│   └── install_*.yml              # Category-specific playbooks
├── docs/                    # Documentation
│   ├── planning/            # Design documents
│   └── dashlane_secrets_setup.md  # Secret structure guide
├── ansible.cfg              # Ansible configuration
├── AGENTS.md                # AI agent development guide
└── README.md                # This file
```

---

## Usage Examples

### Complete Workstation Setup

```bash
# Full setup with profile selection
ansible-playbook playbooks/bootstrap_workstation.yml
```

### Install Specific Categories

```bash
# Just CLI tools
ansible-playbook playbooks/install_cli_tools.yml

# Just cloud CLIs
ansible-playbook playbooks/install_cloud_cli.yml

# Just Kubernetes tools
ansible-playbook playbooks/install_kubernetes_tools.yml

# Just desktop apps
ansible-playbook playbooks/install_desktop_apps.yml
```

### Cloud Demo Environment Setup

```bash
# Setup AWS demo environment (prompts for credentials)
ansible-playbook playbooks/setup_aws_demo.yml

# Setup GCP demo environment
ansible-playbook playbooks/setup_gcp_demo.yml

# Setup Azure demo environment
ansible-playbook playbooks/setup_azure_demo.yml
```

### Run with Specific Profile

```bash
# Force personal profile
ansible-playbook playbooks/bootstrap_workstation.yml -e workstation_profile=personal

# Force work profile
ansible-playbook playbooks/bootstrap_workstation.yml -e workstation_profile=work
```

### Selective Installation with Tags

```bash
# Only foundation and system configuration
ansible-playbook playbooks/bootstrap_workstation.yml --tags "foundation,system"

# Only tools, skip configuration
ansible-playbook playbooks/bootstrap_workstation.yml --tags "tools"

# Specific tool category
ansible-playbook playbooks/bootstrap_workstation.yml --tags "cli"
```

### Check Mode (Dry Run)

```bash
# See what would change without making changes
ansible-playbook playbooks/bootstrap_workstation.yml --check
```

---

## Profiles: Personal vs Work

### Personal Profile

Configured for personal development:
- Personal SSH keys (GitHub, GitLab personal)
- Personal git configuration (personal email)
- Optional personal VPN
- Standard tool installations
- No Red Hat-specific tooling

### Work Profile

Configured for Red Hat work:
- Work SSH keys (Work GitLab, Shadowman git server)
- Work git configuration (Red Hat email)
- Work VPN profiles (Shadowman, root CAs, OpenShift certs)
- Claude Code CLI with Red Hat organization config
- AAP-demo environment tools
- All standard tools

Profile selection happens interactively when you run `bootstrap_workstation.yml`.

---

## Dashlane Secret Management

### Required Secrets in Dashlane

Before running playbooks, ensure these secrets are stored in Dashlane:

#### Personal Profile
- `ssh_key_personal_github` - GitHub SSH private key
- `git_config_personal_name` - Your name for git commits
- `git_config_personal_email` - Your personal email

#### Work Profile
- `ssh_key_work_gitlab` - Work GitLab SSH private key
- `ssh_key_shadowman_git` - Shadowman Git server SSH key
- `git_config_work_name` - Your name for work commits
- `git_config_work_email` - Red Hat email address
- `vpn_shadowman_profile` - Shadowman VPN configuration
- `vpn_shadowman_root_ca` - Root CA certificate
- `openshift_root_ca` - OpenShift cluster root CA
- `claude_code_api_key` - Claude Code API key

See [docs/dashlane_secrets_setup.md](docs/dashlane_secrets_setup.md) for detailed setup instructions.

---

## Special Features

### direnv Safety Checks

When working in `~/Projects/*` directories, direnv will prompt for confirmation before loading environment variables:

```bash
# In ~/Projects/demo-aws-project/.envrc
use_project_env
export AWS_PROFILE=demo-aws-project
export ENV=staging
```

When you `cd` into the directory:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  direnv: Project environment detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current directory: /Users/you/Projects/demo-aws-project
Project: demo-aws-project

Are you in the correct project? (y/N):
```

This prevents accidentally loading the wrong environment variables when switching between similar demo/test projects.

### Cloud Demo Environment Helpers

Quickly setup cloud CLI profiles for demo environments:

```bash
# AWS demo setup
ansible-playbook playbooks/setup_aws_demo.yml
# Prompts for: Account ID, Region, Access Key, Secret Key, Profile Name

# Creates new AWS profile without disrupting existing configurations
# Can be run repeatedly for different demo environments
```

---

## Development

### Adding a New Tool

To add a new tool to an existing category (e.g., adding `ripgrep` to cli_tools):

1. Update `roles/cli_tools/defaults/main.yml`:
   ```yaml
   cli_tools_ripgrep_enabled: true
   cli_tools_packages:
     ripgrep: ripgrep
   ```

2. Create `roles/cli_tools/tasks/install_ripgrep.yml`:
   ```yaml
   ---
   - name: Install ripgrep
     community.general.homebrew:
       name: "{{ cli_tools_packages.ripgrep }}"
       state: "{{ cli_tools_state }}"
   ```

3. Update `roles/cli_tools/tasks/install.yml`:
   ```yaml
   - name: Install ripgrep
     ansible.builtin.import_tasks: install_ripgrep.yml
     when: cli_tools_ripgrep_enabled
   ```

4. Update `roles/cli_tools/meta/argument_specs.yml` to document the new variable.

### Validation & Testing

```bash
# Syntax check
ansible-playbook --syntax-check playbooks/bootstrap_workstation.yml

# Dry run
ansible-playbook --check playbooks/bootstrap_workstation.yml

# Lint roles
ansible-lint roles/*/

# Lint playbooks
ansible-lint playbooks/*.yml

# YAML lint
yamllint roles/ playbooks/
```

---

## Troubleshooting

### Bootstrap Issues

**Command Line Tools not installing:**
```bash
# Try manually:
xcode-select --install
```

**Homebrew not in PATH:**
```bash
# Apple Silicon
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel
eval "$(/usr/local/bin/brew shellenv)"
```

### Dashlane Authentication

**Not logged in:**
```bash
dcli login
```

**Session expired:**
```bash
dcli logout
dcli login
```

### Playbook Failures

**SSH key not found:**
- Verify secret name matches exactly in Dashlane
- Check Dashlane authentication: `dcli whoami`

**Permission denied:**
- Ensure Touch ID for sudo is working
- May need to enter password for first sudo operation

---

## Contributing

This repository follows Red Hat CoP best practices and AGENTS.md standards. See [AGENTS.md](AGENTS.md) for development guidelines.

### Development Workflow

1. Create feature branch
2. Implement changes following AGENTS.md
3. Test locally
4. Run validation: `ansible-lint` and `yamllint`
5. Submit PR

---

## License

MIT

---

## Acknowledgments

- Built with [Red Hat CoP Automation Good Practices](https://redhat-cop.github.io/automation-good-practices/)
- Follows patterns from [Megalith Development Ansible Template](https://github.com/Megalith-Development/Ansible-Template-Repo)
- Inspired by community macOS automation projects

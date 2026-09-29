# Ansible Role: homebrew

Install and configure the Homebrew package manager on macOS systems.

This is a foundational role - all other package-based roles depend on Homebrew being installed.

## Requirements

- macOS (Darwin)
- Apple Command Line Tools installed (`xcode-select --install`)
- Internet connection for downloading Homebrew

## Role Variables

### Installation Settings

```yaml
# Whether to install (present) or remove (absent) Homebrew
homebrew_state: present

# Update Homebrew after installation
homebrew_update: true

# Upgrade all installed packages (use with caution)
homebrew_upgrade_all: false
```

### Path Configuration

```yaml
# Homebrew installation prefix (auto-detected)
# Apple Silicon: /opt/homebrew
# Intel: /usr/local
homebrew_prefix: "{{ '/opt/homebrew' if ansible_architecture == 'arm64' else '/usr/local' }}"

# Homebrew binary path
homebrew_bin: "{{ homebrew_prefix }}/bin/brew"
```

### Shell Integration

```yaml
# Add Homebrew to shell environment
homebrew_configure_shell: true

# Shell profiles to update
homebrew_shell_profiles:
  - "{{ ansible_env.HOME }}/.zprofile"
  - "{{ ansible_env.HOME }}/.zshrc"
```

### Taps and Settings

```yaml
# Homebrew taps to add
homebrew_taps: []
# Example:
# homebrew_taps:
#   - homebrew/cask-fonts
#   - dashlane/tap

# Disable Homebrew analytics
homebrew_disable_analytics: true

# Auto-update when running brew install
homebrew_auto_update: true

# Cask application directory
homebrew_cask_appdir: /Applications
```

## Dependencies

None - this is a foundational role.

## Example Playbook

### Basic Usage

```yaml
---
- name: Install Homebrew
  hosts: localhost
  roles:
    - role: homebrew
```

### With Custom Configuration

```yaml
---
- name: Install and Configure Homebrew
  hosts: localhost
  roles:
    - role: homebrew
      vars:
        homebrew_update: true
        homebrew_disable_analytics: true
        homebrew_taps:
          - homebrew/cask-fonts
          - dashlane/tap
```

### Install Only (No Configuration)

```yaml
---
- name: Install Homebrew Only
  hosts: localhost
  tasks:
    - name: Install Homebrew
      ansible.builtin.import_role:
        name: homebrew
        tasks_from: install
```

### Configure Only (Homebrew Already Installed)

```yaml
---
- name: Configure Homebrew
  hosts: localhost
  tasks:
    - name: Configure Homebrew environment
      ansible.builtin.import_role:
        name: homebrew
        tasks_from: configure
      vars:
        homebrew_taps:
          - homebrew/cask-fonts
```

### Uninstall Homebrew

```yaml
---
- name: Remove Homebrew
  hosts: localhost
  roles:
    - role: homebrew
      vars:
        homebrew_state: absent
```

## Public Functions

This role exposes the following task files as public functions (callable via `tasks_from`):

### install.yml

Install or remove Homebrew.

```yaml
- name: Install Homebrew
  ansible.builtin.import_role:
    name: homebrew
    tasks_from: install
```

### configure.yml

Configure Homebrew environment, taps, and settings.

```yaml
- name: Configure Homebrew
  ansible.builtin.import_role:
    name: homebrew
    tasks_from: configure
  vars:
    homebrew_taps:
      - homebrew/cask-fonts
```

## Tags

- `homebrew` - All homebrew tasks
- `homebrew:validate` - Validation tasks only
- `homebrew:install` - Installation tasks only
- `homebrew:configure` - Configuration tasks only

### Usage with Tags

```bash
# Run only installation
ansible-playbook playbook.yml --tags "homebrew:install"

# Skip configuration
ansible-playbook playbook.yml --skip-tags "homebrew:configure"
```

## Idempotency

This role is fully idempotent:
- Will not reinstall Homebrew if already present
- Safe to run multiple times
- Only updates what has changed

## Architecture Detection

The role automatically detects your Mac's architecture and installs Homebrew in the correct location:

- **Apple Silicon (M1/M2/M3)**: `/opt/homebrew`
- **Intel**: `/usr/local`

## Post-Installation

After running this role:

1. **Restart your shell** or source your profile:
   ```bash
   source ~/.zshrc
   ```

2. **Verify installation**:
   ```bash
   brew --version
   ```

3. **Install packages** using other roles or:
   ```bash
   brew install <package>
   ```

## Troubleshooting

### Command Line Tools Not Found

Error: `Apple Command Line Tools not installed`

**Solution:**
```bash
xcode-select --install
```

Or run the bootstrap script:
```bash
./scripts/bootstrap.sh
```

### Homebrew Not in PATH

If Homebrew installs but isn't found in your PATH:

```bash
# Apple Silicon
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel
eval "$(/usr/local/bin/brew shellenv)"
```

Then restart your shell or:
```bash
source ~/.zshrc
```

### Permission Issues

If you encounter permission errors during installation:

1. Check ownership of Homebrew directories
2. Avoid using `sudo` with Homebrew
3. Review Homebrew's official troubleshooting guide

## License

MIT

## Author

Brian Grimmett

# Terminal Role

Install and configure terminal emulator and fonts for macOS.

## Overview

This role manages installation of:

- **Terminal Emulators**: iTerm2 or Ghostty
- **Nerd Fonts**: Programming fonts with icons and glyphs

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

### Installation Control

```yaml
# Install or remove terminal components
terminal_state: present  # or 'absent'

# Install all components (if false, only install enabled components)
terminal_install_all: true
```

### Terminal Emulator Selection

```yaml
# Terminal emulator to install
terminal_emulator: iterm2  # or 'ghostty'

# Enable iTerm2 installation
terminal_iterm2_enabled: true

# Enable Ghostty installation (newer, GPU-accelerated)
terminal_ghostty_enabled: false
```

### Font Configuration

```yaml
# Install Nerd Fonts for terminal icons and glyphs
terminal_install_nerdfonts: true

# Nerd Fonts to install (Homebrew cask names)
terminal_nerdfonts:
  - font-meslo-lg-nerd-font
  - font-hack-nerd-font
  - font-fira-code-nerd-font
  - font-jetbrains-mono-nerd-font

# Default font to recommend
terminal_default_font: "MesloLGS Nerd Font"
```

## Dependencies

- `homebrew` role

## Public Functions (tasks_from)

```yaml
# Install iTerm2
- ansible.builtin.import_role:
    name: terminal
    tasks_from: install_iterm2

# Install Ghostty
- ansible.builtin.import_role:
    name: terminal
    tasks_from: install_ghostty

# Install Nerd Fonts
- ansible.builtin.import_role:
    name: terminal
    tasks_from: install_nerdfonts
```

## Example Playbook

### Install iTerm2 with Nerd Fonts

```yaml
---
- name: Install terminal
  hosts: localhost
  roles:
    - role: terminal
      vars:
        terminal_emulator: iterm2
```

### Install Ghostty Instead

```yaml
---
- name: Install Ghostty terminal
  hosts: localhost
  roles:
    - role: terminal
      vars:
        terminal_emulator: ghostty
```

### Install Only Nerd Fonts

```yaml
---
- name: Install Nerd Fonts only
  hosts: localhost
  tasks:
    - ansible.builtin.import_role:
        name: terminal
        tasks_from: install_nerdfonts
```

### Custom Nerd Fonts Selection

```yaml
---
- name: Install custom Nerd Fonts
  hosts: localhost
  roles:
    - role: terminal
      vars:
        terminal_nerdfonts:
          - font-fira-code-nerd-font
          - font-jetbrains-mono-nerd-font
```

## Tags

- `validate` - Run validation tasks only
- `install` - Run installation tasks only

## Testing

### Syntax Check

```bash
ansible-playbook --syntax-check playbooks/tests/test_terminal.yml
```

### Dry Run

```bash
ansible-playbook --check playbooks/tests/test_terminal.yml
```

### Execute

```bash
ansible-playbook playbooks/tests/test_terminal.yml
```

## Post-Installation

After installing iTerm2, configure it to use a Nerd Font:

1. Open iTerm2
2. Go to Preferences → Profiles → Text
3. Click "Change Font"
4. Select "MesloLGS Nerd Font" (or your preferred Nerd Font)
5. Set size to 13-14pt for optimal readability

For Ghostty, edit `~/.config/ghostty/config`:

```
font-family = "MesloLGS Nerd Font"
font-size = 13
```

## License

MIT

## Author

Brian Grimmett

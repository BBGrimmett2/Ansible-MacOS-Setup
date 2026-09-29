# Desktop Apps Role

Install and configure desktop applications for macOS.

## Overview

This role manages installation of essential desktop applications:

- **Google Chrome** - Web browser
- **VS Code** - Code editor
- **Cursor** - AI-powered code editor
- **Google Drive** - Cloud storage
- **Rectangle** - Window management
- **DisplayLink Manager** - Multi-monitor support
- **Elgato Camera Hub** - Webcam software (manual download)
- **Elgato Control Center** - Stream Deck/lighting (manual download)
- **Obsidian** - Note-taking app
- **Discord** - Communication platform

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

```yaml
# Install or remove desktop apps
desktop_apps_state: present

# Install all apps
desktop_apps_install_all: true

# Individual app control
desktop_apps_chrome_enabled: true
desktop_apps_vscode_enabled: true
desktop_apps_cursor_enabled: true
desktop_apps_google_drive_enabled: true
desktop_apps_rectangle_enabled: true
desktop_apps_displaylink_enabled: false
desktop_apps_elgato_camera_hub_enabled: false
desktop_apps_elgato_control_center_enabled: false
desktop_apps_obsidian_enabled: true
desktop_apps_discord_enabled: true

# Configure defaults
desktop_apps_configure_defaults: true
desktop_apps_chrome_default_browser: true
desktop_apps_vscode_default_editor: true
```

## Dependencies

- `homebrew` role

## Example Playbook

```yaml
---
- name: Install desktop apps
  hosts: localhost
  roles:
    - role: desktop_apps
```

## Post-Installation

### Set Chrome as Default Browser

```bash
# macOS System Settings → Desktop & Dock → Default web browser
```

### Configure VS Code

```bash
# Install code command
code --install-extension ms-python.python

# Set as default editor for files
```

### Rectangle Keyboard Shortcuts

Default shortcuts after installation:
- `Ctrl + Option + Left Arrow` - Left half
- `Ctrl + Option + Right Arrow` - Right half
- `Ctrl + Option + F` - Fullscreen
- `Ctrl + Option + C` - Center window

### Elgato Downloads

- Camera Hub: https://www.elgato.com/us/en/s/downloads
- Control Center: https://www.elgato.com/us/en/s/downloads

## License

MIT

## Author

Brian Grimmett

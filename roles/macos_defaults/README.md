# Ansible Role: macos_defaults

Configure macOS system preferences using the `defaults` command. Provides comprehensive control over Dock, Finder, keyboard, trackpad, screenshots, and other system settings.

## Requirements

- macOS (Darwin)
- `defaults` command (built-in to macOS)
- `community.general` Ansible collection (for `osx_defaults` module)

## Role Variables

See [defaults/main.yml](defaults/main.yml) for complete list. Key settings:

### Dock Settings

```yaml
macos_dock_autohide: true
macos_dock_position: bottom  # bottom, left, right
macos_dock_tilesize: 48      # 16-128
macos_dock_show_recents: false
```

### Finder Settings

```yaml
macos_finder_show_hidden_files: true
macos_finder_show_extensions: true
macos_finder_show_path_bar: true
macos_finder_default_view: clmv  # icnv=icon, Nlsv=list, clmv=column, Flwv=gallery
```

### Keyboard Settings

```yaml
macos_keyboard_key_repeat: 2          # 1=slow, 2=fast
macos_keyboard_initial_key_repeat: 15  # 15=long, 1=short
```

### Trackpad Settings

```yaml
macos_trackpad_tap_to_click: true
macos_trackpad_tracking_speed: 1.5  # 0.0-3.0
macos_trackpad_natural_scrolling: true
```

### Screenshot Settings

```yaml
macos_screenshots_location: "{{ ansible_env.HOME }}/Desktop"
macos_screenshots_format: png  # png, jpg, gif, pdf, tiff
```

### Application Restart

```yaml
macos_restart_affected_apps: true
macos_apps_to_restart:
  - Finder
  - Dock
  - SystemUIServer
```

## Dependencies

- `community.general` collection

## Example Playbook

### Basic Usage

```yaml
---
- name: Configure macOS preferences
  hosts: localhost
  roles:
    - role: macos_defaults
```

### Custom Configuration

```yaml
---
- name: Configure macOS with custom preferences
  hosts: localhost
  roles:
    - role: macos_defaults
      vars:
        macos_dock_autohide: false
        macos_dock_position: left
        macos_dock_tilesize: 64
        macos_finder_show_hidden_files: true
        macos_trackpad_tap_to_click: true
        macos_screenshots_location: "{{ ansible_env.HOME }}/Pictures/Screenshots"
```

### Configure Specific Components

```yaml
---
- name: Configure Dock only
  hosts: localhost
  tasks:
    - name: Configure Dock
      ansible.builtin.import_role:
        name: macos_defaults
        tasks_from: configure_dock
```

## Public Functions

Call specific configuration tasks via `tasks_from`:

- `configure_dock` - Dock preferences only
- `configure_finder` - Finder preferences only
- `configure_keyboard` - Keyboard preferences only
- `configure_trackpad` - Trackpad preferences only
- `configure_screenshots` - Screenshot preferences only
- `configure_system` - General system preferences only

## Tags

- `macos_defaults` - All tasks
- `macos_defaults:validate` - Validation only
- `macos_defaults:dock` - Dock configuration
- `macos_defaults:finder` - Finder configuration
- `macos_defaults:keyboard` - Keyboard configuration
- `macos_defaults:trackpad` - Trackpad configuration
- `macos_defaults:screenshots` - Screenshot configuration
- `macos_defaults:system` - System configuration

### Usage with Tags

```bash
# Configure Dock only
ansible-playbook playbook.yml --tags "macos_defaults:dock"

# Configure everything except screenshots
ansible-playbook playbook.yml --tags "macos_defaults" --skip-tags "macos_defaults:screenshots"
```

## Notes

- Changes take effect immediately for most settings
- Some settings may require logout/restart to fully apply
- Applications are automatically restarted if `macos_restart_affected_apps: true`
- Role is fully idempotent - safe to run multiple times

## License

MIT

## Author

Brian Grimmett

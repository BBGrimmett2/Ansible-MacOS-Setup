# Database Tools Role

Install and configure database and container management tools for macOS.

## Overview

This role manages installation of:

- **pgAdmin** - PostgreSQL management tool
- **Podman Desktop** - Container management GUI

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

```yaml
# Install or remove database tools
database_tools_state: present

# Install all tools
database_tools_install_all: true

# Individual tool control
database_tools_pgadmin_enabled: true
database_tools_podman_desktop_enabled: true
```

## Dependencies

- `homebrew` role

## Example Playbook

```yaml
---
- name: Install database tools
  hosts: localhost
  roles:
    - role: database_tools
```

## Public Functions

```yaml
# Install pgAdmin only
- ansible.builtin.import_role:
    name: database_tools
    tasks_from: install_pgadmin

# Install Podman Desktop only
- ansible.builtin.import_role:
    name: database_tools
    tasks_from: install_podman_desktop
```

## Post-Installation

### pgAdmin

```bash
# Open pgAdmin
open -a pgAdmin\ 4

# Default: http://127.0.0.1:PORT
```

### Podman Desktop

```bash
# Open Podman Desktop
open -a Podman\ Desktop

# Verify Podman CLI
podman version

# List containers
podman ps

# Run container
podman run -d -p 8080:80 nginx
```

## License

MIT

## Author

Brian Grimmett

# Workstation Manager - macOS App

Native macOS application for managing Ansible-configured workstation, inspired by Red Hat myFleet.

## Status

🚧 **In Development** - Foundation phase

## Overview

Workstation Manager provides a native macOS GUI for:
- Viewing installed components and their status
- Redeploying roles/configurations
- Uninstalling components
- Managing configuration variables
- Viewing Ansible execution logs
- Switching between Personal/Work profiles

## Architecture

**Technology:** Swift + SwiftUI
**Integration:** Executes Ansible playbooks via shell commands
**State Tracking:** `~/.config/workstation-manager/state.json`

## Directory Structure

```
WorkstationManager/
├── Sources/
│   ├── WorkstationManagerApp.swift    # Main app entry
│   ├── Views/
│   │   ├── DashboardView.swift        # Main dashboard
│   │   ├── ComponentListView.swift    # Component list
│   │   ├── ComponentDetailView.swift  # Detail view
│   │   ├── ConfigurationView.swift    # Config editor
│   │   └── LogsView.swift              # Ansible logs
│   ├── Models/
│   │   ├── Component.swift             # Component model
│   │   ├── AnsibleRunner.swift         # Run playbooks
│   │   └── StateManager.swift          # State tracking
│   ├── Services/
│   │   ├── AnsibleService.swift        # Ansible integration
│   │   └── StateService.swift          # State management
│   └── Utils/
│       ├── MenuBarController.swift     # Menu bar icon
│       └── NotificationManager.swift   # Notifications
├── Resources/
│   ├── Assets.xcassets/                # Icons, images
│   └── ansible/                        # Embedded playbooks
└── WorkstationManager.xcodeproj        # Xcode project
```

## Development Phases

### ✅ Phase 1: Foundation (Current)
- [x] Design document created
- [x] State tracking playbook (verify_state.yml)
- [x] Directory structure
- [ ] Xcode project setup
- [ ] Basic UI skeleton

### 🔄 Phase 2: Core Functionality
- [ ] Swift app with menu bar
- [ ] Dashboard view showing component status
- [ ] Read and display state.json
- [ ] Basic component list

### 📋 Phase 3: Ansible Integration
- [ ] Execute playbooks from app
- [ ] Stream output to logs view
- [ ] Update state after operations
- [ ] Error handling

### 🔧 Phase 4: Component Management
- [ ] Redeploy functionality
- [ ] Uninstall functionality
- [ ] Configuration editor
- [ ] Variable overrides

### 📦 Phase 5: DMG Packaging
- [ ] DMG build script
- [ ] Include app in installer
- [ ] First-run wizard
- [ ] Installation workflow

## Prerequisites

- macOS 13.0+ (Ventura or later)
- Xcode 15.0+
- Swift 5.9+
- Ansible installed on system

## Building

```bash
# Open in Xcode
open WorkstationManager.xcodeproj

# Or build from command line
xcodebuild -project WorkstationManager.xcodeproj \
  -scheme WorkstationManager \
  -configuration Release \
  build
```

## State File Format

**Location:** `~/.config/workstation-manager/state.json`

```json
{
  "last_verified": "2026-09-29T10:30:00Z",
  "hostname": "macbook-pro",
  "username": "bgrimmet",
  "profile": "work",
  "os_version": "15.0",
  "architecture": "arm64",
  "components": {
    "homebrew": {
      "installed": true,
      "version": "Homebrew 4.x.x",
      "status": "pass"
    },
    "cli_tools": {
      "installed": true,
      "packages": {
        "jq": true,
        "yq": true,
        "direnv": true,
        "eza": true,
        "bat": true,
        "fd": true,
        "fzf": true,
        "git_delta": true
      },
      "direnv_configured": true,
      "status": "pass"
    }
  }
}
```

## Ansible Integration

The app executes standard Ansible playbooks:

**Verify State:**
```bash
ansible-playbook playbooks/verify_state.yml
```

**Deploy Component:**
```bash
ansible-playbook playbooks/components/cli_tools_deploy.yml
```

**Remove Component:**
```bash
ansible-playbook playbooks/components/cli_tools_remove.yml
```

## Menu Bar Integration

The app runs as a menu bar application with:
- Status icon showing overall health
- Quick access to dashboard
- Update all option
- Preferences

## Screenshots

_Coming soon_

## Design Reference

See detailed design document:
`docs/planning/workstation_manager_app.md`

## License

MIT

## Author

Brandon Grimmet

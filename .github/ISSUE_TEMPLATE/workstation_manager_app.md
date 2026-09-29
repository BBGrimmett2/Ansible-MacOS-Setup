---
name: Workstation Manager macOS App
about: Native macOS GUI for managing Ansible-configured workstation
title: 'Feature: Build Workstation Manager macOS App (myFleet for Personal Workstations)'
labels: enhancement, gui, future
assignees: ''

---

## Overview

Build a native macOS application that provides visibility and control over Ansible-managed workstation configuration, inspired by Red Hat myFleet device management interface.

**Goal:** Self-service portal showing what's installed/configured with ability to redeploy, uninstall, and manage settings through a native GUI.

## Motivation

- **Visibility**: See at a glance what's installed and configured
- **Self-Service**: Redeploy/uninstall components without running Ansible commands
- **Configuration Management**: Edit variables, switch profiles (Personal/Work)
- **Status Monitoring**: Green/Red status indicators like myFleet
- **Ease of Use**: Non-technical users can manage their workstation

## Design Documents

- **Full Design**: `docs/planning/workstation_manager_app.md`
- **State Tracking**: `playbooks/verify_state.yml` (already implemented)
- **App Structure**: `WorkstationManager/README.md`

## Core Features

### Dashboard View
- Status overview with Green/Red indicators
- Last run timestamp
- Profile indicator (Personal/Work)
- Quick actions (Update All, Run Setup)

### Component Management
Categories matching Ansible roles:
- ✓ Foundation (Homebrew, Dashlane)
- ✓ System (macOS Defaults, PAM Security, SSH)
- ✓ CLI Tools (jq, yq, direnv, eza, bat, fd, fzf, git-delta)
- ✓ Terminal (iTerm2/Ghostty, Nerd Fonts)
- ✓ Cloud CLI (AWS, GCP, Azure, GitHub)
- ✓ Kubernetes Tools (oc, kubectl, helm, k9s)
- ✓ Network Tools (VPN, Bruno)
- ✓ Database Tools (pgAdmin, Podman Desktop)
- ✓ Desktop Apps (Chrome, VS Code, Cursor, Rectangle)
- ✓ Development Tools (pre-commit, Claude Code, rhdps)

### Actions Per Component
- 📊 View Status
- 🔄 Redeploy (run Ansible role)
- ❌ Uninstall (state: absent)
- ⚙️ Configure (edit variables)
- 📝 View Logs (Ansible output)

### Menu Bar Integration
- Menu bar icon with status indicator
- Quick access to dashboard
- Notifications for updates/issues

## Technical Stack

- **Language**: Swift
- **Framework**: SwiftUI (native macOS)
- **Integration**: Execute `ansible-playbook` commands
- **State Storage**: `~/.config/workstation-manager/state.json`
- **Minimum macOS**: 13.0+ (Ventura)

## Implementation Phases

### Phase 1: Foundation ✅ COMPLETE
- [x] Design document
- [x] State tracking playbook (`playbooks/verify_state.yml`)
- [x] Directory structure (`WorkstationManager/`)
- [x] State file format defined

### Phase 2: Swift App Skeleton
- [ ] Create Xcode project
- [ ] Implement menu bar icon (NSStatusItem)
- [ ] Create main window with SwiftUI
- [ ] Dashboard view (static mockup)
- [ ] Component list view (static)

### Phase 3: State Reading
- [ ] StateManager to read state.json
- [ ] Display real component status
- [ ] Color coding (Green/Red/Yellow)
- [ ] Last updated timestamp

### Phase 4: Ansible Integration
- [ ] AnsibleService to execute playbooks
- [ ] Stream output to logs view
- [ ] Parse Ansible results
- [ ] Update UI on completion
- [ ] Error handling

### Phase 5: Component Actions
- [ ] Redeploy button → run component playbook
- [ ] Uninstall button → run with state: absent
- [ ] Configuration editor (YAML)
- [ ] Variable overrides to local file

### Phase 6: Advanced Features
- [ ] Profile switcher (Personal/Work)
- [ ] Full setup wizard
- [ ] Update all functionality
- [ ] Scheduled verification
- [ ] macOS notifications

### Phase 7: DMG Packaging
- [ ] Create DMG build script
- [ ] Include app in installer
- [ ] First-run setup wizard
- [ ] Code signing
- [ ] Notarization

## File Structure

```
WorkstationManager/
├── WorkstationManager.xcodeproj
├── Sources/
│   ├── WorkstationManagerApp.swift
│   ├── Views/
│   │   ├── DashboardView.swift
│   │   ├── ComponentListView.swift
│   │   ├── ComponentDetailView.swift
│   │   ├── ConfigurationView.swift
│   │   └── LogsView.swift
│   ├── Models/
│   │   ├── Component.swift
│   │   ├── AnsibleRunner.swift
│   │   └── StateManager.swift
│   ├── Services/
│   │   ├── AnsibleService.swift
│   │   └── StateService.swift
│   └── Utils/
│       ├── MenuBarController.swift
│       └── NotificationManager.swift
└── Resources/
    ├── Assets.xcassets/
    └── ansible/ (embedded playbooks)
```

## User Experience Flow

### First Launch
1. Open app from Applications
2. Welcome wizard prompts for profile (Personal/Work)
3. Runs full verification (`playbooks/verify_state.yml`)
4. Shows dashboard with current state

### Daily Use
1. Menu bar icon shows overall status
2. Click to open dashboard
3. See component status at a glance
4. Click component for details
5. Click "Redeploy" if needed
6. View logs of execution
7. Status updates automatically

### Redeploy Flow
1. User clicks "Redeploy" on CLI Tools component
2. App runs: `ansible-playbook playbooks/components/cli_tools_deploy.yml`
3. Streams output to logs viewer
4. On completion, runs `verify_state.yml`
5. Updates UI with new status

## Example State File

```json
{
  "last_verified": "2026-09-29T10:30:00Z",
  "hostname": "macbook-pro",
  "profile": "work",
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
        "direnv": true
      },
      "status": "pass"
    }
  }
}
```

## Similar Projects (Inspiration)

- **Red Hat myFleet**: Enterprise device management dashboard
- **Cakebrew**: GUI for Homebrew package management
- **Ansible Tower/AAP**: Job templates and execution history
- **macOS System Preferences**: Native settings interface

## Benefits

- **Visibility**: See what's configured without running commands
- **Safety**: Verify before making changes
- **Convenience**: Click to redeploy instead of command line
- **Tracking**: History of what was installed when
- **User-Friendly**: Non-technical users can manage their machine

## Open Questions

- [ ] Should app bundle Ansible, or require external installation?
- [ ] Support for remote management (multiple machines)?
- [ ] Cloud backup of configurations?
- [ ] Telemetry/analytics (privacy-respecting)?

## Success Criteria

- [ ] App installs via DMG drag-and-drop
- [ ] Dashboard shows accurate component status
- [ ] Redeploy button successfully runs Ansible roles
- [ ] Configuration changes persist across launches
- [ ] App works offline (local Ansible execution)
- [ ] First-time user can complete setup without CLI

## Future Enhancements

- Multi-machine management
- Cloud configuration sync
- Rollback to previous configurations
- Configuration drift detection
- Integration with Dashlane GUI
- Remote API for automation

---

**Priority**: Future Enhancement
**Effort**: Large (multi-week project)
**Dependencies**: All Ansible roles complete, state tracking verified
**Skills Needed**: Swift, SwiftUI, macOS development

# Workstation Manager App - Design Document

**Inspired by:** Red Hat myFleet device management interface

**Purpose:** Native macOS application providing visibility and control over Ansible-managed workstation configuration

---

## Overview

A native macOS menu bar/dock app that shows what's installed and configured on your workstation, similar to how Red Hat myFleet displays compliance policies and software status.

## Core Features

### 1. Dashboard View
- **Status Overview**: Green/Red indicators for each configured component
- **Last Run**: Timestamp of last Ansible execution
- **Profile**: Personal vs Work configuration
- **Compliance**: All checks passing/failing

### 2. Component Management

**Categories (matching our roles):**
- ✓ Foundation (Homebrew, Dashlane)
- ✓ System (macOS Defaults, PAM Security, SSH)
- ✓ CLI Tools (jq, yq, direnv, eza, bat, fd, fzf, git-delta)
- ✓ Terminal (iTerm2/Ghostty, Nerd Fonts)
- ✓ Cloud CLI (AWS, GCP, Azure, GitHub)
- ✓ Kubernetes Tools (oc, kubectl, helm, k9s)
- ✓ Network Tools (VPN, Bruno)
- ✓ Database Tools (pgAdmin, Podman Desktop)
- ✓ Desktop Apps (Chrome, VS Code, Cursor, Rectangle, etc.)
- ✓ Development Tools (pre-commit, Claude Code, git config, rhdps)

**Actions per component:**
- 📊 **View Status** - Check if installed/configured
- 🔄 **Redeploy** - Run Ansible role again
- ❌ **Uninstall** - Remove component (state: absent)
- ⚙️ **Configure** - View/edit role variables
- 📝 **Logs** - View last Ansible run output

### 3. Configuration Panel
- View current role variables
- Edit variables (saved to local overrides)
- Reset to defaults
- Profile switcher (Personal/Work)

### 4. Operations
- **Run Full Setup** - Execute bootstrap_workstation.yml
- **Update All** - Upgrade all packages/tools
- **Validate Setup** - Run validation playbook
- **Export State** - Save current configuration
- **Import State** - Restore from export

---

## Technical Architecture

### Technology Stack

**Frontend:**
- **Language**: Swift
- **Framework**: SwiftUI (native macOS UI)
- **Menu Bar**: NSStatusItem for menu bar presence
- **Dock App**: Optional dock icon with notifications

**Backend:**
- **Ansible Integration**: Execute playbooks via `ansible-playbook` command
- **State Storage**: SQLite database + JSON state files
- **Process Management**: Run Ansible in background, stream output

### State Tracking

**State File:** `~/.config/workstation-manager/state.json`

```json
{
  "last_run": "2026-09-29T10:30:00Z",
  "profile": "work",
  "components": {
    "homebrew": {
      "installed": true,
      "version": "4.x.x",
      "last_configured": "2026-09-29T10:00:00Z",
      "status": "pass"
    },
    "cli_tools": {
      "installed": true,
      "packages": ["jq", "yq", "direnv", "eza", "bat", "fd", "fzf", "git-delta"],
      "last_configured": "2026-09-29T10:15:00Z",
      "status": "pass"
    },
    "terminal": {
      "installed": true,
      "emulator": "iterm2",
      "fonts_installed": true,
      "last_configured": "2026-09-29T10:20:00Z",
      "status": "pass"
    }
    // ... more components
  }
}
```

**Verification Playbook:** `playbooks/verify_state.yml`
- Runs after each operation
- Updates state.json
- Returns status of all components

### App Structure

```
WorkstationManager.app/
├── Contents/
│   ├── MacOS/
│   │   └── WorkstationManager (Swift executable)
│   ├── Resources/
│   │   ├── Assets.xcassets/ (icons, images)
│   │   ├── ansible/ (embedded playbooks)
│   │   └── config.plist
│   └── Info.plist
```

**Swift App Structure:**
```
Sources/
├── WorkstationManagerApp.swift (main app)
├── Views/
│   ├── DashboardView.swift (main window)
│   ├── ComponentListView.swift (list of roles)
│   ├── ComponentDetailView.swift (individual role detail)
│   ├── ConfigurationView.swift (edit variables)
│   └── LogsView.swift (Ansible output)
├── Models/
│   ├── Component.swift (component state model)
│   ├── AnsibleRunner.swift (execute playbooks)
│   └── StateManager.swift (read/write state.json)
├── Services/
│   ├── AnsibleService.swift (run playbooks)
│   └── StateService.swift (track state)
└── Utils/
    ├── MenuBarController.swift (menu bar icon)
    └── NotificationManager.swift (macOS notifications)
```

---

## User Interface Design

### Menu Bar Icon
```
☰ Workstation Manager
├── 📊 Open Dashboard
├── ✓ Status: All Green (or ⚠️ 3 Issues)
├── 🔄 Update All
├── ⚙️ Preferences
└── 🚪 Quit
```

### Main Window - Dashboard Tab
```
┌─────────────────────────────────────────────────────────┐
│ Workstation Manager                    [Personal ▼] [⚙] │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Last Updated: 35 minutes ago            [🔄 Run Setup]  │
│                                                           │
│  Status Overview                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ ✓ Foundation          ✓ CLI Tools                 │  │
│  │ ✓ System Config       ✓ Terminal                  │  │
│  │ ✓ Cloud CLI           ✓ Kubernetes Tools           │  │
│  │ ✓ Desktop Apps        ✓ Development Tools          │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Components Tab
```
┌─────────────────────────────────────────────────────────┐
│ Components                    [🔍 Search]  [+ Add New]   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ✓ Homebrew                                  [⚙] [🔄] [×]│
│    Package manager - Installed 4.x.x                     │
│                                                           │
│  ✓ CLI Tools                                 [⚙] [🔄] [×]│
│    8 tools installed (jq, yq, direnv, eza, bat...)       │
│                                                           │
│  ✓ Terminal                                  [⚙] [🔄] [×]│
│    iTerm2 with Nerd Fonts                                │
│                                                           │
│  ✓ Cloud CLI                                 [⚙] [🔄] [×]│
│    AWS, GCP, Azure, GitHub CLIs                          │
│                                                           │
│  ⚠ Development Tools                         [⚙] [🔄] [×]│
│    Claude Code not configured                            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Component Detail View (clicking a component)
```
┌─────────────────────────────────────────────────────────┐
│ ← Back to Components          CLI Tools                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Status: ✓ Installed and Configured                      │
│  Last Updated: 2 hours ago                                │
│                                                           │
│  Installed Packages:                                      │
│    ✓ jq - JSON processor                                 │
│    ✓ yq - YAML processor                                 │
│    ✓ direnv - Per-directory env vars (Safety: ON)        │
│    ✓ eza - Modern ls replacement                         │
│    ✓ bat - Modern cat with syntax highlighting           │
│    ✓ fd - Modern find replacement                        │
│    ✓ fzf - Fuzzy finder                                  │
│    ✓ git-delta - Git diff pager                          │
│                                                           │
│  Configuration:                                           │
│    cli_tools_direnv_safety_enabled: true                 │
│    cli_tools_direnv_projects_path: ~/Projects            │
│                                                           │
│  [View Logs] [Edit Config] [🔄 Redeploy] [× Uninstall]   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Ansible Integration

### State Verification Playbook

**File:** `playbooks/verify_state.yml`

```yaml
---
- name: Verify Workstation State
  hosts: localhost
  gather_facts: true

  tasks:
    - name: Check Homebrew status
      ansible.builtin.stat:
        path: "{{ homebrew_prefix }}/bin/brew"
      register: homebrew_status

    - name: Check CLI tools
      ansible.builtin.shell: which {{ item }}
      loop: [jq, yq, direnv, eza, bat, fd, fzf, delta]
      register: cli_tools_status
      failed_when: false
      changed_when: false

    # ... more checks

    - name: Write state file
      ansible.builtin.copy:
        content: "{{ state_data | to_nice_json }}"
        dest: "{{ ansible_env.HOME }}/.config/workstation-manager/state.json"
      vars:
        state_data:
          last_run: "{{ ansible_date_time.iso8601 }}"
          components: "{{ component_status }}"
```

### Component Playbooks

Each component gets dedicated playbooks in `playbooks/components/`:

```
playbooks/components/
├── homebrew_deploy.yml
├── homebrew_remove.yml
├── cli_tools_deploy.yml
├── cli_tools_remove.yml
├── terminal_deploy.yml
├── terminal_remove.yml
└── ...
```

**Pattern:**
```yaml
# playbooks/components/cli_tools_deploy.yml
---
- name: Deploy CLI Tools
  hosts: localhost
  roles:
    - cli_tools
  post_tasks:
    - ansible.builtin.import_playbook: ../verify_state.yml
```

### App Execution Flow

1. **User clicks "Redeploy" on CLI Tools**
2. App runs: `ansible-playbook playbooks/components/cli_tools_deploy.yml`
3. Streams output to logs view
4. On completion, runs `playbooks/verify_state.yml`
5. Reads updated `state.json`
6. Updates UI to show new status

---

## DMG Installer Integration

### DMG Contents
```
WorkstationSetup.dmg
├── Workstation Manager.app
├── Install.command (bootstrap script)
├── README.html
└── .background/ (DMG background image)
```

### Install Workflow

1. **User mounts DMG**
2. **Drag app to Applications**
3. **Run Install.command** which:
   - Installs Ansible prerequisites
   - Runs bootstrap_workstation.yml
   - Launches Workstation Manager.app
   - Shows initial setup wizard

### First Launch Wizard

```
┌─────────────────────────────────────────────────────────┐
│                 Welcome to Workstation Manager           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Select your workstation profile:                        │
│                                                           │
│    ( ) Personal                                           │
│        • Personal SSH keys                                │
│        • Personal git config                              │
│        • No work-specific tools                           │
│                                                           │
│    (•) Work (Red Hat)                                     │
│        • Work SSH keys                                    │
│        • Red Hat git config                               │
│        • Claude Code CLI                                  │
│        • AAP demo environment                             │
│        • OpenShift certificates                           │
│                                                           │
│                            [Continue]                     │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: State Tracking (Foundation)
- [ ] Create state.json schema
- [ ] Create verify_state.yml playbook
- [ ] Add post-task to all roles to update state
- [ ] Test state tracking manually

### Phase 2: Swift App Skeleton
- [ ] Create Xcode project
- [ ] Implement menu bar icon
- [ ] Create dashboard view (static)
- [ ] Show hardcoded component list

### Phase 3: Ansible Integration
- [ ] AnsibleService to run playbooks
- [ ] Stream output to logs view
- [ ] Parse state.json
- [ ] Update UI from state

### Phase 4: Component Management
- [ ] Implement redeploy functionality
- [ ] Implement uninstall functionality
- [ ] Configuration editor
- [ ] Logs viewer

### Phase 5: DMG Packaging
- [ ] Create DMG build script
- [ ] Add app to DMG
- [ ] Create Install.command
- [ ] Design DMG background
- [ ] Test installation workflow

### Phase 6: Advanced Features
- [ ] Notifications for updates
- [ ] Scheduled verification
- [ ] Export/import configurations
- [ ] Profile switching
- [ ] Update checking

---

## Development Approach

### Option 1: Native Swift App (Recommended)
**Pros:**
- Native macOS UI/UX
- Menu bar integration
- Fast, lightweight
- Code signing for distribution

**Cons:**
- Requires Swift/Xcode knowledge
- More complex initial setup

### Option 2: Electron App
**Pros:**
- Web technologies (HTML/CSS/JS)
- Faster prototyping
- Cross-platform (if needed)

**Cons:**
- Larger app size
- Less native feel
- More resource intensive

### Option 3: Python + PyQt/Tkinter
**Pros:**
- Easier for Python developers
- Quick prototyping

**Cons:**
- Requires Python runtime
- Less native appearance
- Distribution complexity

**Recommendation:** Swift/SwiftUI for native macOS experience

---

## File Locations

### App Data
- **State File**: `~/.config/workstation-manager/state.json`
- **Logs**: `~/.config/workstation-manager/logs/`
- **Overrides**: `~/.config/workstation-manager/overrides.yml`
- **Cache**: `~/.cache/workstation-manager/`

### Ansible Integration
- **Playbooks**: `/Applications/Workstation Manager.app/Contents/Resources/ansible/`
- **Roles**: Symlink to `~/ansible-macos-setup/roles/`
- **Inventory**: `~/.config/workstation-manager/inventory.yml`

---

## Security Considerations

1. **Privilege Escalation**: Some operations require sudo
   - Prompt for password when needed
   - Use macOS authorization framework
   - Never store passwords

2. **Code Signing**: Sign the app for distribution
   - Apple Developer ID
   - Notarization for Gatekeeper

3. **Ansible Execution**: Run with user permissions
   - No arbitrary command execution
   - Whitelist allowed playbooks
   - Validate inputs

---

## Future Enhancements

- [ ] Cloud backup of configuration
- [ ] Multi-machine management
- [ ] Integration with Dashlane for secret viewing
- [ ] Scheduled maintenance windows
- [ ] Rollback to previous configuration
- [ ] Configuration drift detection
- [ ] Remote management API
- [ ] CLI companion tool

---

## Next Steps

1. **Create state tracking system** (verify_state.yml playbook)
2. **Build Swift app prototype** (dashboard + component list)
3. **Implement Ansible integration** (run playbooks from app)
4. **Create component playbooks** (deploy/remove for each role)
5. **DMG packaging** (create distributable installer)
6. **Testing** (on fresh macOS VM)
7. **Documentation** (user guide, screenshots)

---

## Inspiration References

- **Red Hat myFleet**: Policy compliance dashboard
- **Homebrew GUI**: Cakebrew (visual package manager)
- **Ansible Tower/AAP**: Job templates and execution
- **macOS System Preferences**: Native settings panels

This app bridges the gap between manual Ansible execution and enterprise device management, providing a self-service portal for workstation configuration.

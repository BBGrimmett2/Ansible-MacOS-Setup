# macOS Ansible Workstation Setup Plan

## Phase 0: Bootstrap & DMG Installer (Zero-to-Hero)
The goal of this phase is to get the machine ready to run Ansible securely without hardcoding secrets, starting from absolute zero.

*   [ ] **Create DMG Release Artifact:** Package the initial bootstrapping process into a downloadable macOS `.dmg` installer.
    *   *Implementation Note:* This DMG should contain an executable application wrapper (e.g., an AppleScript applet) that automatically fetches the latest `install.sh` from the repository's `main` branch and runs it in the terminal. This allows you to download a single file from a GitHub Release on a fresh Mac to kick off the entire process.
*   [ ] Create the remote `install.sh` script (triggered by the DMG) to automate initial installations:
    *   [ ] Install Apple Command Line Tools (`xcode-select --install`).
    *   [ ] Install Homebrew.
    *   [ ] Install Python3 (via Homebrew).
    *   [ ] Install Ansible (inside a Python `venv`).
    *   [ ] Install [Dashlane CLI](https://cli.dashlane.com/) via Homebrew for pulling secrets dynamically (avoids storing passwords/keys in Git).
    *   [ ] Pull down the Ansible Git repository.

## Phase 1: Ansible Automation Plan (The Playbooks)

### 1. System Configurations & Ergonomics
*   [ ] Set macOS Defaults (Dock settings, Show hidden files, Show file extensions).
*   [ ] Configure Touch ID for `sudo` (modify `/etc/pam.d/sudo` to include `pam_tid.so`).
*   [ ] Setup `pam_u2f` for YubiKey hardware authentication support.
*   [ ] Set Default File Associations (Route `.yml`, `.json`, `.sh`, `.py` to open in VS Code/Cursor).
*   [ ] Install a Menu Bar Manager (e.g., Ice or Bartender) to clean up the macOS menu bar.

### 2. Terminal & CLI Environment
*   [ ] Install Terminal Emulator (e.g., iTerm2 or Ghostty).
*   [ ] Install ZSH & configure it as the default shell via `chsh`.
*   [ ] Install NerdFonts (for terminal icons).
*   [ ] Install CLI Quality-of-Life Tools:
    *   [ ] `jq` / `yq` (JSON/YAML parsing).
    *   [ ] `direnv` (Per-directory environment variables).
    *   [ ] `eza` or `lsd` (Modern `ls` replacement with icons).
    *   [ ] `bat` (Modern `cat` replacement with syntax highlighting).
    *   [ ] `fd` (Modern `find` replacement).
    *   [ ] `git-delta` (Syntax-highlighting pager for git diffs).
    *   [ ] `fzf` (Fuzzy finder).

### 3. Git, Secrets, & SSH Configuration
*   [ ] Configure Global Git settings (username, email, core editor).
*   [ ] Install `pre-commit` (Git hook framework for `ansible-lint` and `yamllint`).
*   [ ] Deploy `~/.ssh/config` file.
*   [ ] Pull and deploy SSH keys dynamically using Dashlane CLI:
    *   [ ] Keys for Shadowman Git server.
    *   [ ] Keys for Work GitLab.

### 4. Cloud CLI & Development Tools
*   [ ] Install AWS CLI.
*   [ ] Install Google Cloud CLI.
*   [ ] Install Azure CLI.
*   [ ] Install GitHub CLI (`gh`).
*   [ ] Configure Claude Code CLI (Needs specific instructions pulled into README).
*   [ ] Install AAP-Demo environment tools (from [RedHatOfficial/aap-demo](https://github.com/RedHatOfficial/aap-demo)).

### 5. OpenShift & Kubernetes Toolkit
*   [ ] Install `oc` (OpenShift CLI).
*   [ ] Install `kubectl`.
*   [ ] Install `helm` (Kubernetes package manager).
*   [ ] Install `k9s` (Terminal UI for cluster management).
*   [ ] Install `kubectx` and `kubens` (Fast context/namespace switching).
*   [ ] Install `stern` (Multi-pod/container log tailing).

### 6. Network, VPN, & API Inspection
*   [ ] Install OpenVPN Client.
*   [ ] Install `bind` tools (provides `dig` and `nslookup` for DNS troubleshooting).
*   [ ] Install Bruno (Desktop API client for testing REST endpoints).
*   [ ] Configure VPN and Root CAs:
    *   [ ] Starbase: Root CA + VPN Profile.
    *   [ ] Shadowman: Root CA + VPN Profile + OpenShift Root CA.

### 7. Databases & Container Platforms
*   [ ] Install Podman Desktop.
*   [ ] Install PGAdmin.

### 8. Desktop Applications & Utilities
*   [ ] Configure `mas` (Mac App Store CLI) for any App Store-only apps.
*   [ ] Install Google Chrome & Set as Default Browser.
*   [ ] Install VS Code & Set as Default Code Editor.
*   [ ] Install Cursor.
*   [ ] Install Google Drive.
*   [ ] Install Rectangle (Window Management).
*   [ ] Install DisplayLink Manager.
*   [ ] Install Elgato Camera Hub.
*   [ ] Install Elgato Control Center.
*   [ ] Install Obsidian.
*   [ ] Install Discord.

## Phase 2: ZSH Configuration Map
Design the Ansible playbook to template the `~/.zshrc` file with these blocks:
1.  **Path Configurations:** Add Homebrew, Python VENVs, and standard binaries to `$PATH`.
2.  **Environment Variables:** Export defaults (e.g., `export EDITOR="code"`).
3.  **Tool Hooks:**
    *   `eval "$(direnv hook zsh)"`
    *   `eval "$(fzf --zsh)"`
4.  **Aliases:**
    *   `alias ls='lsd'` or `alias ls='eza --icons'`
    *   `alias cat='bat'`
    *   `alias k='kubectl'`
    *   `alias oc='oc'`

## Phase 3: Uninstallation & Revert Strategy
*   **Design Rule:** For every tool in Phase 1, ensure the Ansible role supports a `state: absent` variable (or similar toggle) to easily uninstall the app and remove its configuration files.
*   **Cleanup Tasks:** Add tasks to remove symlinks, clean up `~/Library/Application Support/` folders for GUI apps, and purge cached `.dmg` installers.

---

## Reference Links
*   **Homebrew:** https://brew.sh/
*   **Google Drive:** https://ipv4.google.com/intl/en_zm/drive/download/
*   **Google Drive Help:** https://support.google.com/drive/answer/12178485?hl=en
*   **GitHub CLI:** https://cli.github.com/
*   **Rectangle:** https://rectangleapp.com/
*   **DisplayLink:** https://www.synaptics.com/products/displaylink-graphics/downloads/macos
*   **Elgato Camera Hub:** https://edge.elgato.com/egc/macos/echm/2.3.0/CameraHub_2.3.0.7295.pkg
*   **Elgato Control Center:** https://edge.elgato.com/egc/macos/eccm/1.9/ElgatoControlCenter-1.9.20829.app.zip
*   **Obsidian:** https://obsidian.md/
*   **Discord:** https://discord.com/download
*   **VS Code:** https://code.visualstudio.com/
*   **Cursor:** https://cursor.com/
*   **AWS CLI:** https://aws.amazon.com/cli/
*   **GCP CLI:** https://cloud.google.com/cli
*   **Azure CLI:** https://learn.microsoft.com/en-us/cli/azure/?view=azure-cli-latest
*   **OpenVPN:** https://openvpn.net/client/
*   **PGAdmin:** https://www.pgadmin.org/
*   **Podman Desktop:** https://podman-desktop.io/
*   **Dashlane CLI:** https://cli.dashlane.com/
*   **AAP-Demo Repo:** https://github.com/RedHatOfficial/aap-demo
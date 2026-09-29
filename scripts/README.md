# Bootstrap Scripts

This directory contains the bootstrap script that prepares a fresh macOS system for Ansible automation.

## bootstrap.sh

The main bootstrap script that installs all prerequisites needed to run Ansible playbooks.

### What it does

1. **Apple Command Line Tools** - Installs Xcode CLI tools (required for git, compilers, etc.)
2. **Homebrew** - Installs the Homebrew package manager
3. **Python 3** - Installs Python 3 via Homebrew
4. **Ansible** - Creates a Python virtual environment and installs Ansible
5. **Dashlane CLI** - Installs Dashlane CLI for secure secret management
6. **Ansible Collections** - Installs required Galaxy collections

### Usage

#### First-time setup (fresh Mac)

```bash
# Download the bootstrap script
curl -fsSL https://raw.githubusercontent.com/bgrimmet/Ansible-MacOS-Setup/main/scripts/bootstrap.sh -o bootstrap.sh

# Make it executable
chmod +x bootstrap.sh

# Run it
./bootstrap.sh
```

#### From cloned repository

```bash
# Navigate to the repository
cd /path/to/Ansible-MacOS-Setup

# Run the bootstrap script
./scripts/bootstrap.sh
```

### After Bootstrap

Once the bootstrap script completes successfully:

1. **Authenticate with Dashlane**:
   ```bash
   dcli login
   ```

2. **Activate the Ansible virtual environment**:
   ```bash
   source ~/venv-ansible/bin/activate
   ```

3. **Run the main workstation setup**:
   ```bash
   cd /path/to/Ansible-MacOS-Setup
   ansible-playbook playbooks/bootstrap_workstation.yml
   ```

### Configuration

Before running, you may want to update these variables in `bootstrap.sh`:

- `REPO_URL` - Your repository URL (if different)
- `REPO_DIR` - Where to clone the repository
- `VENV_PATH` - Python virtual environment location

### Idempotency

The bootstrap script is idempotent - it's safe to run multiple times. It will:
- Skip installations if tools are already present
- Update existing installations where appropriate
- Not break existing configurations

### Troubleshooting

#### Command Line Tools installation hangs

If the Xcode Command Line Tools installation dialog doesn't appear:
```bash
# Cancel the script (Ctrl+C) and try manually:
xcode-select --install
# Then re-run the bootstrap script
```

#### Homebrew not in PATH

If Homebrew installs but isn't found:
```bash
# Apple Silicon (M1/M2/M3)
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel
eval "$(/usr/local/bin/brew shellenv)"
```

#### Dashlane CLI issues

If Dashlane CLI doesn't install properly:
```bash
# Install manually:
brew tap dashlane/tap
brew install dashlane-cli
```

### Future Enhancements

Planned improvements:
- [ ] DMG installer package for easy distribution
- [ ] Automatic git repository detection
- [ ] Pre-flight network connectivity checks
- [ ] Backup of existing configurations
- [ ] Support for resuming interrupted installations

# Installation Scripts

This directory contains the web installer script that automates complete macOS workstation setup from zero to fully configured.

## install.sh

The main web installer that handles everything from prerequisites to complete workstation automation.

### What it does

1. **System Validation** - Checks macOS platform, admin rights, internet connection, disk space
2. **Xcode Command Line Tools** - Installs Apple developer tools (required for git, compilers)
3. **Homebrew** - Installs the Homebrew package manager
4. **Python 3** - Installs Python 3 via Homebrew
5. **Ansible Virtual Environment** - Creates Python venv and installs Ansible
6. **Dashlane CLI** - Installs and configures Dashlane CLI for secret management
7. **Repository Clone** - Clones this repository to `~/ansible-macos-setup`
8. **Galaxy Collections** - Installs required Ansible collections
9. **Workstation Bootstrap** - Automatically runs the full workstation setup playbook

### One-Line Installation (Recommended)

Run this command on a fresh macOS machine:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh)"
```

**Alternative (shorter):**
```bash
curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh | bash
```

### Manual Installation (From Cloned Repository)

If you prefer to clone first:

```bash
# Clone the repository
git clone https://github.com/BBGrimmett2/Ansible-MacOS-Setup.git
cd Ansible-MacOS-Setup

# Run the installer
./scripts/install.sh
```

### What Happens

The script is fully automated and will:

1. Validate your system meets requirements
2. Install all prerequisites (Xcode CLI, Homebrew, Python, Ansible, Dashlane CLI)
3. Clone the repository (if not already cloned)
4. Attempt Dashlane authentication (`dcli configure`)
5. Install required Ansible Galaxy collections
6. Run the `bootstrap_workstation.yml` playbook with profile selection prompt
7. Display next steps

**No user interaction required** except:
- Xcode CLI Tools installation popup (click "Install")
- Dashlane authentication (follow prompts in browser)
- Profile selection (personal/work)
- Sudo password when prompted

### Configuration

Constants defined in `install.sh`:

- `REPO_URL` - Repository URL (`https://github.com/BBGrimmett2/Ansible-MacOS-Setup.git`)
- `REPO_DIR` - Clone destination (`~/ansible-macos-setup`)
- `VENV_DIR` - Python venv location (`~/venv-ansible`)
- `PYTHON_MIN_VERSION` - Minimum Python version (`3.9`)
- `ANSIBLE_MIN_VERSION` - Minimum Ansible version (`2.15`)

### Idempotency

The installer is idempotent and safe to run multiple times:
- Skips installations if tools are already present
- Updates repository if already cloned
- Reconfigures shell profiles if needed
- Won't break existing configurations

### Troubleshooting

#### Xcode Command Line Tools not installing

If the installation popup doesn't appear:
```bash
# Try manually:
xcode-select --install
# Then re-run install.sh
```

#### Homebrew not in PATH after installation

The script configures your shell automatically, but for the current session:
```bash
# Apple Silicon
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel
eval "$(/usr/local/bin/brew shellenv)"

# Or reload your shell
source ~/.zshrc
```

#### Dashlane authentication fails

If `dcli configure` doesn't complete:
```bash
# Try manually after installation:
dcli configure

# Then verify:
dcli status
```

#### Script interruption

If the script is interrupted (Ctrl+C), it's safe to re-run:
```bash
# Continue from where it left off
./scripts/install.sh
```

The script will skip completed steps and continue.

### After Installation

Once complete, your workstation is fully configured. To use Homebrew tools in your current terminal session:

```bash
source ~/.zshrc
```

Or open a new terminal window.

### Repository Location

The repository is cloned to:
```
~/ansible-macos-setup
```

Ansible virtual environment is at:
```
~/venv-ansible
```

### Running Specific Playbooks

After installation, you can run category-specific playbooks:

```bash
cd ~/ansible-macos-setup

# Activate Ansible venv
source ~/venv-ansible/bin/activate

# Run specific categories
ansible-playbook playbooks/install_cli_tools.yml
ansible-playbook playbooks/install_cloud_cli.yml
ansible-playbook playbooks/install_kubernetes_tools.yml

# Setup cloud demo environments
ansible-playbook playbooks/setup_aws_demo.yml
ansible-playbook playbooks/setup_gcp_demo.yml
```

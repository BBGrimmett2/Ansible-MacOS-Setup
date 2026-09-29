#!/bin/bash
# =============================================================================
# macOS Workstation Bootstrap Script
# =============================================================================
# Purpose: Zero-to-Ansible automation - prepares a fresh macOS system to run
#          Ansible playbooks by installing all prerequisites.
#
# What this script installs:
#   1. Apple Command Line Tools (xcode-select)
#   2. Homebrew package manager
#   3. Python 3 (via Homebrew)
#   4. Ansible (in a Python virtual environment)
#   5. Dashlane CLI (for secure secret management)
#
# After running this script, you'll be ready to run the main Ansible playbooks.
# =============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_PATH="$HOME/venv-ansible"
REPO_URL="https://github.com/BBGrimmett2/Ansible-MacOS-Setup.git"
REPO_DIR="$HOME/ansible-macos-setup"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# Phase 0: Pre-flight Checks
# =============================================================================

print_header "macOS Workstation Bootstrap"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only."
    print_error "Detected OS: $OSTYPE"
    exit 1
fi

print_success "Running on macOS"

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion)
print_info "macOS version: $MACOS_VERSION"

# =============================================================================
# Phase 1: Install Apple Command Line Tools
# =============================================================================

print_header "Phase 1: Apple Command Line Tools"

if xcode-select -p >/dev/null 2>&1; then
    print_success "Command Line Tools already installed at: $(xcode-select -p)"
else
    print_info "Installing Apple Command Line Tools..."
    print_warning "A dialog will appear - please click 'Install' and accept the license."

    # Trigger the installer
    xcode-select --install 2>/dev/null || true

    # Wait for installation to complete
    print_info "Waiting for Command Line Tools installation to complete..."
    until xcode-select -p >/dev/null 2>&1; do
        sleep 5
    done

    print_success "Command Line Tools installed successfully"
fi

# Accept Xcode license if needed
if ! /usr/bin/xcrun --version >/dev/null 2>&1; then
    print_warning "You may need to accept the Xcode license. Running: sudo xcodebuild -license accept"
    sudo xcodebuild -license accept 2>/dev/null || true
fi

# =============================================================================
# Phase 2: Install Homebrew
# =============================================================================

print_header "Phase 2: Homebrew Package Manager"

if command_exists brew; then
    print_success "Homebrew already installed: $(brew --version | head -n 1)"
    print_info "Updating Homebrew..."
    brew update
else
    print_info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for current session
    if [[ $(uname -m) == "arm64" ]]; then
        # Apple Silicon
        eval "$(/opt/homebrew/bin/brew shellenv)"
        BREW_PREFIX="/opt/homebrew"
    else
        # Intel
        eval "$(/usr/local/bin/brew shellenv)"
        BREW_PREFIX="/usr/local"
    fi

    print_success "Homebrew installed successfully"
fi

# Ensure Homebrew is in PATH
if ! command_exists brew; then
    print_error "Homebrew was installed but is not in PATH. Please restart your terminal."
    exit 1
fi

# =============================================================================
# Phase 3: Install Python 3
# =============================================================================

print_header "Phase 3: Python 3"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python 3 already installed: $PYTHON_VERSION"
else
    print_info "Installing Python 3 via Homebrew..."
    brew install python@3.12
    print_success "Python 3 installed successfully"
fi

# Verify Python installation
if ! command_exists python3; then
    print_error "Python 3 installation failed or is not in PATH"
    exit 1
fi

# =============================================================================
# Phase 4: Create Python Virtual Environment and Install Ansible
# =============================================================================

print_header "Phase 4: Ansible Installation"

if [[ -d "$VENV_PATH" ]]; then
    print_success "Virtual environment already exists at: $VENV_PATH"
else
    print_info "Creating Python virtual environment at: $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
print_info "Upgrading pip..."
pip install --quiet --upgrade pip

# Install Ansible
if command_exists ansible; then
    ANSIBLE_VERSION=$(ansible --version | head -n 1)
    print_success "Ansible already installed: $ANSIBLE_VERSION"
    print_info "Upgrading Ansible..."
    pip install --quiet --upgrade ansible
else
    print_info "Installing Ansible..."
    pip install --quiet ansible
    print_success "Ansible installed successfully"
fi

# Verify Ansible installation
ANSIBLE_VERSION=$(ansible --version | head -n 1)
print_success "Ansible version: $ANSIBLE_VERSION"

# =============================================================================
# Phase 5: Install Dashlane CLI
# =============================================================================

print_header "Phase 5: Dashlane CLI (Secret Management)"

if command_exists dcli; then
    print_success "Dashlane CLI already installed: $(dcli --version 2>/dev/null || echo 'version unknown')"
else
    print_info "Installing Dashlane CLI via Homebrew..."

    # Add Dashlane tap if not already added
    brew tap dashlane/tap 2>/dev/null || true

    # Install Dashlane CLI
    brew install dashlane-cli

    print_success "Dashlane CLI installed successfully"
fi

# Check if Dashlane is installed
if ! command_exists dcli; then
    print_warning "Dashlane CLI installation may have issues. You can install it manually later."
else
    print_info "Dashlane CLI is ready. You'll need to authenticate before running playbooks."
    print_info "Run: dcli login"
fi

# =============================================================================
# Phase 6: Clone Ansible Repository (if not already in it)
# =============================================================================

print_header "Phase 6: Ansible Repository"

# Check if we're already in the repository
if [[ -d ".git" ]] && [[ -f "AGENTS.md" ]]; then
    print_success "Already in Ansible repository: $(pwd)"
    REPO_DIR=$(pwd)
else
    if [[ -d "$REPO_DIR" ]]; then
        print_success "Repository already cloned at: $REPO_DIR"
    else
        print_info "Cloning Ansible repository..."
        git clone "$REPO_URL" "$REPO_DIR"
        print_success "Repository cloned successfully"
    fi
fi

# =============================================================================
# Phase 7: Install Ansible Galaxy Collections
# =============================================================================

print_header "Phase 7: Ansible Galaxy Collections"

if [[ -f "collections/requirements.yml" ]]; then
    print_info "Installing Ansible Galaxy collections..."
    ansible-galaxy collection install -r collections/requirements.yml
    print_success "Collections installed successfully"
else
    print_warning "No collections/requirements.yml found. Skipping collection installation."
fi

# =============================================================================
# Bootstrap Complete
# =============================================================================

print_header "Bootstrap Complete!"

echo ""
print_success "All prerequisites installed successfully!"
echo ""
print_info "Next steps:"
echo "  1. Authenticate with Dashlane CLI:"
echo "     ${BLUE}dcli login${NC}"
echo ""
echo "  2. Navigate to the repository (if not already there):"
echo "     ${BLUE}cd $REPO_DIR${NC}"
echo ""
echo "  3. Activate the Ansible virtual environment:"
echo "     ${BLUE}source $VENV_PATH/bin/activate${NC}"
echo ""
echo "  4. Run the main bootstrap playbook:"
echo "     ${BLUE}ansible-playbook playbooks/bootstrap_workstation.yml${NC}"
echo ""
print_info "To activate the virtual environment in future sessions:"
echo "  ${BLUE}source $VENV_PATH/bin/activate${NC}"
echo ""

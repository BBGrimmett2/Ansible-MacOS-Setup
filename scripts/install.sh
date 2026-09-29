#!/bin/bash
# =============================================================================
# Workstation Setup - Web Installer
# =============================================================================
# Purpose: Zero-to-configured macOS workstation automation
#
# Usage (recommended):
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh)"
#
# Usage (shorter):
#   curl -fsSL https://raw.githubusercontent.com/BBGrimmett2/Ansible-MacOS-Setup/main/scripts/install.sh | bash
#
# This script bootstraps a fresh macOS machine from zero to fully configured
# workstation by installing prerequisites and running Ansible automation.
#
# Author: Brian Grimmett
# Company: Starbase Engineering
# Repository: https://github.com/BBGrimmett2/Ansible-MacOS-Setup
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

readonly REPO_URL="https://github.com/BBGrimmett2/Ansible-MacOS-Setup.git"
readonly REPO_DIR="${HOME}/ansible-macos-setup"
readonly VENV_DIR="${HOME}/venv-ansible"
readonly PYTHON_MIN_VERSION="3.9"
readonly ANSIBLE_MIN_VERSION="2.15"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# =============================================================================
# UI Helper Functions
# =============================================================================

print_banner() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}  macOS Workstation Setup${RESET}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}▸ ${BOLD}$1${RESET}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────${RESET}"
}

print_step() {
    echo -e "  ${GREEN}✓${RESET} $1"
}

print_info() {
    echo -e "  ${CYAN}ℹ${RESET} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${RESET} $1"
}

print_error() {
    echo -e "  ${RED}✗${RESET} $1" >&2
}

print_success() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${GREEN}${BOLD}  ✓ $1${RESET}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
}

print_fatal() {
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${RED}${BOLD}  ✗ Fatal Error: $1${RESET}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
    exit 1
}

spinner() {
    local pid=$1
    local message=$2
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i+1) % 10 ))
        echo -ne "\r  ${CYAN}${spin:$i:1}${RESET} ${message}..."
        sleep 0.1
    done

    wait "$pid"
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo -e "\r  ${GREEN}✓${RESET} ${message}... Done"
    else
        echo -e "\r  ${RED}✗${RESET} ${message}... Failed"
        return $exit_code
    fi
}

# =============================================================================
# Validation Functions
# =============================================================================

check_macos() {
    print_section "Validating System Requirements"

    if [[ "$(uname)" != "Darwin" ]]; then
        print_fatal "This installer is for macOS only (detected: $(uname))"
    fi
    print_step "Running on macOS $(sw_vers -productVersion)"
}

check_admin_rights() {
    if ! groups | grep -q '\badmin\b'; then
        print_fatal "Current user is not an administrator. Please run as admin user."
    fi
    print_step "User has administrator privileges"
}

check_internet() {
    if ! ping -c 1 -W 2 github.com &>/dev/null; then
        print_fatal "No internet connection. Please connect to the internet and try again."
    fi
    print_step "Internet connection active"
}

check_disk_space() {
    local available_gb=$(df -g / | awk 'NR==2 {print $4}')
    if (( available_gb < 10 )); then
        print_warning "Low disk space: ${available_gb}GB available (10GB recommended)"
    else
        print_step "Sufficient disk space: ${available_gb}GB available"
    fi
}

# =============================================================================
# Installation Functions
# =============================================================================

install_xcode_cli_tools() {
    print_section "Installing Xcode Command Line Tools"

    if xcode-select -p &>/dev/null; then
        print_step "Xcode Command Line Tools already installed"
        return 0
    fi

    print_info "Installing Xcode Command Line Tools (this may take several minutes)..."
    print_info "A popup will appear - please click 'Install'"

    # Trigger installation
    xcode-select --install 2>/dev/null || true

    # Wait for installation
    print_info "Waiting for installation to complete..."
    until xcode-select -p &>/dev/null; do
        sleep 5
    done

    # Accept license
    sudo xcodebuild -license accept 2>/dev/null || true

    print_step "Xcode Command Line Tools installed successfully"
}

configure_homebrew_shell() {
    # Determine shell configuration file
    local shell_rc=""
    if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *"bash"* ]]; then
        shell_rc="$HOME/.bash_profile"
    else
        print_warning "Unknown shell, skipping shell configuration"
        return 0
    fi

    # Determine Homebrew path
    local brew_path=""
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        brew_path="/opt/homebrew"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        brew_path="/usr/local"
    else
        return 0
    fi

    # Check if shellenv already in rc file
    if grep -q "brew shellenv" "$shell_rc" 2>/dev/null; then
        print_step "Homebrew already configured in $shell_rc"
        return 0
    fi

    # Add Homebrew to shell configuration
    print_info "Adding Homebrew to $shell_rc"
    {
        echo ""
        echo "# Homebrew"
        echo "eval \"\$(${brew_path}/bin/brew shellenv)\""
    } >> "$shell_rc"

    print_step "Homebrew configured in $shell_rc"
}

install_homebrew() {
    print_section "Installing Homebrew Package Manager"

    # Check if Homebrew binary exists (check file directly, not PATH)
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        # Apple Silicon - already installed
        eval "$(/opt/homebrew/bin/brew shellenv)"
        print_step "Homebrew already installed at /opt/homebrew/bin/brew"
        print_info "Skipping Homebrew update (Ansible will manage packages)"
        configure_homebrew_shell
        return 0
    elif [[ -f "/usr/local/bin/brew" ]]; then
        # Intel - already installed
        eval "$(/usr/local/bin/brew shellenv)"
        print_step "Homebrew already installed at /usr/local/bin/brew"
        print_info "Skipping Homebrew update (Ansible will manage packages)"
        configure_homebrew_shell
        return 0
    fi

    print_info "Installing Homebrew..."

    # Download and run Homebrew installer
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" </dev/null &
    spinner $! "Installing Homebrew"

    # Add Homebrew to PATH for current session
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        # Apple Silicon
        eval "$(/opt/homebrew/bin/brew shellenv)"
        print_step "Homebrew installed (Apple Silicon)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        # Intel
        eval "$(/usr/local/bin/brew shellenv)"
        print_step "Homebrew installed (Intel)"
    else
        print_fatal "Homebrew installation failed"
    fi

    # Configure shell for future sessions
    configure_homebrew_shell
}

install_python() {
    print_section "Setting Up Python Environment"

    # Check if Python 3 is available
    if ! command -v python3 &>/dev/null; then
        print_info "Installing Python via Homebrew..."
        brew install python3 &
        spinner $! "Installing Python"
    fi

    local python_version=$(python3 --version | awk '{print $2}')
    print_step "Python ${python_version} available"

    # Check version meets minimum requirement
    local version_check=$(python3 -c "import sys; print(sys.version_info >= (${PYTHON_MIN_VERSION%.*}, ${PYTHON_MIN_VERSION#*.}))")
    if [[ "$version_check" != "True" ]]; then
        print_fatal "Python ${PYTHON_MIN_VERSION}+ required (found ${python_version})"
    fi
}

create_ansible_venv() {
    print_section "Creating Ansible Virtual Environment"

    if [[ -d "$VENV_DIR" ]]; then
        print_step "Virtual environment already exists at ${VENV_DIR}"
    else
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR" &
        spinner $! "Creating virtual environment"
    fi

    # Activate venv
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel &>/dev/null &
    spinner $! "Upgrading pip"

    print_step "Virtual environment ready"
}

install_ansible() {
    print_section "Installing Ansible"

    # Activate venv
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"

    if command -v ansible-playbook &>/dev/null; then
        local ansible_version=$(ansible --version | head -n1 | awk '{print $2}' | cut -d']' -f1 | tr -d '[')
        print_step "Ansible ${ansible_version} already installed"
        return 0
    fi

    print_info "Installing Ansible and dependencies..."
    pip install ansible &>/dev/null &
    spinner $! "Installing Ansible"

    local ansible_version=$(ansible --version | head -n1 | awk '{print $2}' | cut -d']' -f1 | tr -d '[')
    print_step "Ansible ${ansible_version} installed successfully"
}

install_dashlane_cli() {
    print_section "Installing Dashlane CLI"

    if command -v dcli &>/dev/null; then
        print_step "Dashlane CLI already installed"
        return 0
    fi

    print_info "Installing Dashlane CLI via Homebrew..."
    brew install dashlane/tap/dashlane-cli &>/dev/null &
    spinner $! "Installing Dashlane CLI"

    # Ensure dcli is available in current shell
    hash -r 2>/dev/null || true

    # Verify installation
    if ! command -v dcli &>/dev/null; then
        print_warning "Dashlane CLI installed but not in PATH. You may need to restart your shell."
        print_info "Try running: hash -r"
    else
        print_step "Dashlane CLI installed successfully"
    fi
}

clone_repository() {
    print_section "Cloning Ansible Repository"

    if [[ -d "$REPO_DIR" ]]; then
        print_step "Repository already exists at ${REPO_DIR}"

        # Update repository
        print_info "Updating repository..."
        (cd "$REPO_DIR" && git pull origin main) &>/dev/null &
        spinner $! "Updating repository"

        return 0
    fi

    print_info "Cloning repository from ${REPO_URL}..."
    git clone "$REPO_URL" "$REPO_DIR" &>/dev/null &
    spinner $! "Cloning repository"

    print_step "Repository cloned to ${REPO_DIR}"
}

authenticate_dashlane() {
    print_section "Authenticating Dashlane CLI"

    # Ensure dcli is available
    if ! command -v dcli &>/dev/null; then
        print_warning "Dashlane CLI not found in PATH"
        print_warning "You can authenticate later by running: dcli sync"
        return 0
    fi

    # Check if already authenticated
    local already_authenticated=false
    local dashlane_user=""

    if dcli whoami &>/dev/null; then
        already_authenticated=true
        dashlane_user=$(dcli whoami 2>/dev/null || echo "unknown")
        print_step "Dashlane CLI already authenticated (user: ${dashlane_user})"
        echo ""
        read -p "Re-authenticate with different account? (y/N): " reauth_choice

        if [[ ! "$reauth_choice" =~ ^[Yy]$ ]]; then
            print_info "Keeping current Dashlane authentication"
            return 0
        fi

        print_info "Proceeding with re-authentication..."
    else
        print_info "Dashlane authentication required for secret management"
        print_info "Skip now and authenticate later by running: dcli sync"
        echo ""
        read -p "Authenticate now? (Y/n): " auth_choice

        if [[ "$auth_choice" =~ ^[Nn]$ ]]; then
            print_warning "Skipping Dashlane authentication"
            print_warning "Run 'dcli sync' before running playbooks that need secrets"
            return 0
        fi
    fi

    # Run dcli sync - it will automatically open browser
    echo ""
    if ! dcli sync; then
        echo ""
        print_warning "Dashlane authentication failed"
        print_warning "You can authenticate later by running: dcli sync"
        print_info "Press Enter to continue..."
        read -r
    else
        echo ""
        print_step "Dashlane CLI authenticated successfully"
    fi
}

# =============================================================================
# Ansible Galaxy Collections
# =============================================================================

install_galaxy_collections() {
    print_section "Installing Ansible Galaxy Collections"

    # Activate venv
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"

    # Change to repository directory
    cd "$REPO_DIR"

    # Check if requirements file exists
    if [[ ! -f "collections/requirements.yml" ]]; then
        print_info "No collections/requirements.yml found, skipping collection installation"
        return 0
    fi

    # Check if collections list is empty
    if grep -q "collections: \[\]" collections/requirements.yml; then
        print_info "No collections defined in requirements.yml, skipping installation"
        return 0
    fi

    print_info "Installing required Ansible collections..."

    # Install collections and show output
    if ansible-galaxy collection install -r collections/requirements.yml; then
        print_step "Ansible collections installed successfully"
    else
        print_warning "Galaxy collections installation had issues (non-fatal, continuing)"
    fi
}

# =============================================================================
# Ansible Playbook Execution
# =============================================================================

run_ansible_playbook() {
    print_section "Running Ansible Workstation Bootstrap"

    # Activate venv
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"

    # Change to repository directory
    cd "$REPO_DIR"

    print_info "Starting Ansible playbook execution..."
    print_info "You will be prompted to select your workstation profile"
    echo ""

    # Run the bootstrap playbook
    if ! ansible-playbook playbooks/bootstrap_workstation.yml; then
        print_fatal "Ansible playbook execution failed. Check the output above for errors."
    fi

    print_success "Workstation Bootstrap Complete!"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    print_banner

    # Pre-flight checks
    check_macos
    check_admin_rights
    check_internet
    check_disk_space

    # Install prerequisites
    install_xcode_cli_tools
    install_homebrew
    install_python
    create_ansible_venv
    install_ansible
    install_dashlane_cli

    # Setup repository
    clone_repository
    authenticate_dashlane
    install_galaxy_collections

    # Run Ansible automation
    run_ansible_playbook

    # Final instructions
    print_section "Next Steps"
    print_info "1. Restart your terminal to load new shell configuration"
    print_info "2. Run 'source ~/.zshrc' to reload your shell environment"
    print_info "3. Verify installations: brew list, kubectl version, etc."
    echo ""
    print_info "For cloud demo environments, run:"
    print_info "  cd ${REPO_DIR}"
    print_info "  ansible-playbook playbooks/setup_aws_demo.yml"
    print_info "  ansible-playbook playbooks/setup_gcp_demo.yml"
    print_info "  ansible-playbook playbooks/setup_azure_demo.yml"
    echo ""
    print_info "Repository: ${REPO_DIR}"
    print_info "Virtual environment: ${VENV_DIR}"
    echo ""

    print_success "All done! Your workstation is ready to use."
}

# =============================================================================
# Error Handling
# =============================================================================

# Trap errors and cleanup
trap 'print_fatal "Installation interrupted or failed"' ERR INT TERM

# Run main function
main "$@"

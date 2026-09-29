# Dashlane Secrets Quick Reference

Quick cheat sheet for creating and managing Dashlane secrets for workstation automation.

## Required Secrets by Profile

### Personal Profile

| Secret Name | Type | Purpose | Generate Command |
|------------|------|---------|------------------|
| `ssh_key_personal_github` | Secure Note | GitHub SSH auth | `ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_github` |

### Work Profile

| Secret Name | Type | Purpose | Generate Command |
|------------|------|---------|------------------|
| `ssh_key_work_gitlab` | Secure Note | GitLab SSH auth | `ssh-keygen -t ed25519 -C "work@company.com" -f ~/.ssh/id_work_gitlab` |
| `ssh_key_shadowman_git` | Secure Note | Red Hat Shadowman SSH | `ssh-keygen -t ed25519 -C "you@redhat.com" -f ~/.ssh/id_shadowman` |
| `vpn_shadowman_profile` | Secure Note | Shadowman VPN | Obtain from IT/admin (.ovpn file) |
| `cert_shadowman_root_ca` | Secure Note | Shadowman CA cert | Obtain from IT/admin (PEM certificate) |

## Quick Setup Steps

### 1. Generate SSH Key

```bash
# Personal GitHub
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_github

# Work GitLab
ssh-keygen -t ed25519 -C "work@company.com" -f ~/.ssh/id_work_gitlab

# Red Hat Shadowman
ssh-keygen -t ed25519 -C "you@redhat.com" -f ~/.ssh/id_shadowman
```

### 2. Create Dashlane Secure Note

1. Open Dashlane
2. Click **+ Add New** → **Secure Note**
3. **Title:** Use exact name from table above (e.g., `ssh_key_personal_github`)
4. **Content:** Paste entire private key:
   ```bash
   cat ~/.ssh/id_github  # Copy output
   ```
5. Click **Save**

### 3. Add Public Key to Service

```bash
# Copy public key
cat ~/.ssh/id_github.pub

# Then add to:
# - GitHub: Settings → SSH and GPG keys
# - GitLab: Preferences → SSH Keys
# - Red Hat: Your git server settings
```

### 4. Test Access

```bash
# Authenticate with Dashlane CLI
dcli configure
dcli status

# Test secret retrieval
dcli read ssh_key_personal_github --output raw

# Should output:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ...
# -----END OPENSSH PRIVATE KEY-----
```

## Searching Secrets by Category

Use grep to filter secrets by category prefix:

```bash
# Find all SSH keys
dcli note list | grep "^ssh_key_"

# Find all personal profile secrets
dcli note list | grep "_personal"

# Find all work profile secrets
dcli note list | grep "_work"

# Find all Shadowman-related secrets
dcli note list | grep "shadowman"

# Find all certificates
dcli note list | grep -E "cert_|_ca$"

# Find all VPN profiles
dcli note list | grep "^vpn_"

# Find all configuration files
dcli note list | grep "config_"
```

## Shadowman Quick Setup

Complete Shadowman infrastructure setup (work profile):

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "you@redhat.com" -f ~/.ssh/temp_shadowman -N ""

# 2. Create secrets in Dashlane
dcli note add --title "ssh_key_shadowman_git" --content "$(cat ~/.ssh/temp_shadowman)"
dcli note add --title "vpn_shadowman_profile" --content "$(cat /path/to/shadowman.ovpn)"
dcli note add --title "cert_shadowman_root_ca" --content "$(cat /path/to/shadowman-ca.pem)"

# 3. Add SSH public key to Shadowman git server
cat ~/.ssh/temp_shadowman.pub  # Copy and add to git server

# 4. Clean up temporary key
rm ~/.ssh/temp_shadowman*

# 5. Run Ansible playbook
ansible-playbook playbooks/bootstrap_workstation.yml \
  -e workstation_profile=work \
  --ask-become-pass
```

See [SHADOWMAN_SETUP.md](SHADOWMAN_SETUP.md) for complete documentation.

## Common Commands

```bash
# Authentication
dcli configure              # Initial setup
dcli status                 # Check auth status
dcli sync                   # Sync vault

# Reading secrets
dcli read <secret_name> --output raw

# Listing secrets
dcli note list             # List all secure notes
dcli password list         # List all logins

# Creating secrets (via CLI)
dcli note add --title "<name>" --content "$(cat /path/to/file)"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Secret not found | Check exact title (case-sensitive), run `dcli sync` |
| Authentication failed | Run `dcli configure` again |
| Permission denied | Check private key permissions: `chmod 600 ~/.ssh/id_*` |
| Missing BEGIN/END markers | Re-copy entire key including headers |

## Expected Secret Format

All SSH keys must be stored as the complete private key with headers:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
[... many lines of base64 encoded content ...]
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==
-----END OPENSSH PRIVATE KEY-----
```

**Important:**
- Include `-----BEGIN OPENSSH PRIVATE KEY-----` header
- Include `-----END OPENSSH PRIVATE KEY-----` footer
- Include ALL lines between headers
- No extra whitespace or characters

## Naming Convention

```
ssh_key_<profile>_<service>

Examples:
  ssh_key_personal_github     ✓ Good
  ssh_key_work_gitlab         ✓ Good
  GitHub SSH Key              ✗ Bad (not standardized)
  ssh-key-github              ✗ Bad (wrong separator)
```

## Sensitive Configuration Files

You can also store complete config files in Dashlane (for files with sensitive endpoints, API keys, etc.):

| File | Secret Name | Enable With |
|------|------------|-------------|
| ~/.ssh/config | `ssh_config_personal` or `ssh_config_work` | `ssh_config_from_dashlane: true` |
| ~/.zshrc | `zshrc_personal` or `zshrc_work` | `shell_environment_zshrc_from_dashlane: true` |
| ~/.gitconfig | `gitconfig_personal` or `gitconfig_work` | `development_tools_gitconfig_from_dashlane: true` |

See [SENSITIVE_FILES_GUIDE.md](SENSITIVE_FILES_GUIDE.md) for detailed examples and setup.

## Full Documentation

For complete details, see:
- [DASHLANE_SECRETS_SETUP.md](DASHLANE_SECRETS_SETUP.md) - SSH keys and credentials
- [SENSITIVE_FILES_GUIDE.md](SENSITIVE_FILES_GUIDE.md) - Configuration files

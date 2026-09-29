# Dashlane Secrets Setup Guide

This guide documents all secrets required for the macOS workstation automation, their format, and how to create them in Dashlane.

## Table of Contents

- [Overview](#overview)
- [Required Secrets](#required-secrets)
- [Sensitive Configuration Files](#sensitive-configuration-files)
- [Optional Secrets](#optional-secrets)
- [How to Create Secrets in Dashlane](#how-to-create-secrets-in-dashlane)
- [Naming Conventions](#naming-conventions)
- [Testing Secrets](#testing-secrets)
- [Troubleshooting](#troubleshooting)

## Overview

This repository uses [Dashlane CLI](https://cli.dashlane.com/) to securely retrieve secrets without hardcoding them in the repository. Secrets are stored in your Dashlane vault and retrieved during playbook execution.

### Why Dashlane?

- **No hardcoded credentials** in git repository
- **Secure storage** with Dashlane's encryption
- **Easy rotation** - update in Dashlane, no code changes needed
- **Profile-specific** - different secrets for personal vs work profiles

## Required Secrets

These secrets are **required** for the automation to work properly, depending on your selected profile.

### SSH Keys

SSH keys are stored as **Secure Notes** in Dashlane with the private key content as the note body.

#### `ssh_key_personal_github`

**Profile:** Personal
**Type:** Secure Note
**Purpose:** SSH authentication for personal GitHub repositories

**How to create:**
1. Generate SSH key pair (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_github
   ```

2. In Dashlane:
   - Create a new **Secure Note**
   - Title: `ssh_key_personal_github`
   - Content: Paste the **entire private key** (from `~/.ssh/id_github`)
   - Save the note

3. Add public key to GitHub:
   - Copy public key: `cat ~/.ssh/id_github.pub`
   - Go to GitHub → Settings → SSH and GPG keys → New SSH key
   - Paste and save

**Example content format:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
...
[many lines of base64 encoded key]
...
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==
-----END OPENSSH PRIVATE KEY-----
```

#### `ssh_key_work_gitlab`

**Profile:** Work
**Type:** Secure Note
**Purpose:** SSH authentication for work GitLab repositories

**How to create:**
1. Generate SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "your_work_email@company.com" -f ~/.ssh/id_work_gitlab
   ```

2. In Dashlane:
   - Create a new **Secure Note**
   - Title: `ssh_key_work_gitlab`
   - Content: Paste the **entire private key** (from `~/.ssh/id_work_gitlab`)
   - Save the note

3. Add public key to GitLab:
   - Copy public key: `cat ~/.ssh/id_work_gitlab.pub`
   - Go to GitLab → Preferences → SSH Keys → Add new key
   - Paste and save

#### `ssh_key_shadowman_git`

**Profile:** Work
**Type:** Secure Note
**Purpose:** SSH authentication for Red Hat Shadowman internal git repositories

**How to create:**
1. Generate SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "your_redhat_email@redhat.com" -f ~/.ssh/id_shadowman
   ```

2. In Dashlane:
   - Create a new **Secure Note**
   - Title: `ssh_key_shadowman_git`
   - Content: Paste the **entire private key** (from `~/.ssh/id_shadowman`)
   - Save the note

3. Add public key to Red Hat git:
   - Copy public key: `cat ~/.ssh/id_shadowman.pub`
   - Add to your Red Hat git server's SSH keys settings

## Sensitive Configuration Files

Instead of using templates or hardcoding configuration files, you can store complete sensitive config files in Dashlane. This is useful when files contain:
- Private hostnames/endpoints
- API keys or tokens
- Company-specific configurations
- Credential helpers

### Supported Configuration Files

| Config File | Personal Secret | Work Secret | Enable Variable |
|------------|----------------|-------------|-----------------|
| SSH config | `ssh_config_personal` | `ssh_config_work` | `ssh_config_from_dashlane: true` |
| ZSH config | `zshrc_personal` | `zshrc_work` | `shell_environment_zshrc_from_dashlane: true` |
| Git config | `gitconfig_personal` | `gitconfig_work` | `development_tools_gitconfig_from_dashlane: true` |

### Quick Setup

1. **Export your current config:**
   ```bash
   cat ~/.ssh/config    # or ~/.zshrc or ~/.gitconfig
   ```

2. **Create Dashlane Secure Note:**
   - Title: Use exact name from table (e.g., `ssh_config_personal`)
   - Content: Paste complete file content
   - Save and sync

3. **Enable in Ansible:**
   ```yaml
   # In group_vars/localhost.yml or as extra-vars
   ssh_config_from_dashlane: true
   shell_environment_zshrc_from_dashlane: true
   development_tools_gitconfig_from_dashlane: true
   ```

4. **Run playbook:**
   ```bash
   ansible-playbook playbooks/bootstrap_workstation.yml
   ```

For complete documentation including examples and troubleshooting, see:
**[SENSITIVE_FILES_GUIDE.md](SENSITIVE_FILES_GUIDE.md)**

## Shadowman Infrastructure Secrets (Work Profile)

These secrets are **required for the work profile** to fully configure Red Hat Shadowman infrastructure access including VPN and certificate management.

### VPN Profiles

#### `vpn_shadowman_profile`

**Profile:** Work
**Type:** Secure Note
**Purpose:** OpenVPN profile for Red Hat Shadowman VPN
**Status:** ✅ **ACTIVE** - Deployed to `~/.vpn/shadowman.ovpn`

**Format:** Complete `.ovpn` file content including certificates

**Example:**
```
client
dev tun
proto udp
remote vpn.example.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca [inline]
cert [inline]
key [inline]
remote-cert-tls server
cipher AES-256-CBC
verb 3
...
```

### SSL/TLS Certificates

#### `cert_shadowman_root_ca`

**Profile:** Work
**Type:** Secure Note
**Purpose:** Root CA certificate for Shadowman infrastructure (HTTPS/TLS validation)
**Status:** ✅ **ACTIVE** - Installed to system keychain

**Format:** PEM-encoded certificate

**Example:**
```
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKxxxxxxxxxxxxxx
...
-----END CERTIFICATE-----
```

#### `openshift_root_ca`

**Type:** Secure Note
**Purpose:** Root CA certificate for OpenShift clusters

**Format:** PEM-encoded certificate

### Login Credentials

Credentials are stored as **Login** entries in Dashlane with username and password fields.

**Example naming:** `api_service_login`, `database_admin_login`

**Fields:**
- **Title:** Descriptive name
- **Username:** The username/login ID
- **Password:** The password
- **URL:** (Optional) Associated service URL

## How to Create Secrets in Dashlane

### Using Dashlane Web/Desktop App

1. **Open Dashlane** (web app or desktop application)

2. **For SSH Keys (Secure Notes):**
   - Click **+ Add New** → **Secure Note**
   - **Title:** Use exact naming convention (e.g., `ssh_key_personal_github`)
   - **Content:** Paste the entire private key including BEGIN/END markers
   - **Category:** (Optional) Create a category like "SSH Keys"
   - Click **Save**

3. **For Credentials (Logins):**
   - Click **+ Add New** → **Login**
   - **Title:** Use naming convention (e.g., `github_token`)
   - **Username:** Your username or email
   - **Password:** Your password or token
   - **URL:** (Optional) Associated service
   - Click **Save**

4. **Sync your vault:**
   - Ensure changes are synced to all devices
   - In desktop app: Check sync status in top-right
   - In CLI: Run `dcli sync`

### Using Dashlane CLI

You can also create secrets via CLI:

```bash
# Sync vault first
dcli sync

# Create a secure note (for SSH keys)
dcli note create \
  --title "ssh_key_personal_github" \
  --content "$(cat ~/.ssh/id_github)"

# Verify it was created
dcli read ssh_key_personal_github --output raw
```

## Naming Conventions

Following consistent naming makes secrets easy to find, maintain, and extend. All secrets use a standardized pattern for maximum clarity and searchability.

### Pattern Structure

```
<category>_<profile|purpose>_<service|resource>
```

**Principles:**
- **Lowercase with underscores** (snake_case) for Ansible compatibility
- **Searchable prefixes** for filtering: `dcli note list | grep <prefix>`
- **Profile qualification**: `personal` / `work` / `shadowman`
- **Clear service identification**

### SSH Keys
**Format:** `ssh_key_<profile>_<service>`

**Examples:**
- `ssh_key_personal_github` - Personal GitHub key
- `ssh_key_personal_gitlab` - Personal GitLab key
- `ssh_key_work_gitlab` - Work GitLab key
- `ssh_key_shadowman_git` - Red Hat Shadowman git key

**Search:** `dcli note list | grep "^ssh_key_"`

### Configuration Files
**Format:** `<tool>config_<profile>`

**Examples:**
- `ssh_config_personal` - Personal SSH client config
- `ssh_config_work` - Work SSH client config
- `gitconfig_personal` - Personal git config
- `gitconfig_work` - Work git config
- `zshrc_personal` - Personal shell config
- `zshrc_work` - Work shell config

**Search:** `dcli note list | grep "config_"`

### VPN Profiles
**Format:** `vpn_<environment>_profile`

**Examples:**
- `vpn_shadowman_profile` - Red Hat Shadowman VPN (.ovpn file)
- `vpn_personal_nordvpn` - Personal VPN profile

**Search:** `dcli note list | grep "^vpn_"`

### Certificates
**Format:** `cert_<purpose>_<type>`

**Examples:**
- `cert_shadowman_root_ca` - Shadowman root CA certificate
- `openshift_root_ca` - OpenShift cluster root CA
- `cert_company_signing` - Company code signing certificate

**Search:** `dcli note list | grep -E "cert_|_ca$"`

### Credentials/Tokens
**Format:** `<service>_<profile>_<type>` or `<service>_<type>`

**Examples:**
- `github_personal_token` - Personal GitHub PAT
- `github_work_token` - Work GitHub PAT
- `aws_demo_credentials` - AWS demo environment
- `vault_shadowman_token` - Shadowman Vault token

**Search:** `dcli note list | grep "_token$\|_credentials$"`

### Best Practices

1. **Use lowercase** with underscores (snake_case)
2. **Be descriptive** but concise
3. **Include profile** (personal/work) when applicable
4. **Include service** name for clarity
5. **Be consistent** across your vault
6. **Use searchable prefixes** to enable filtering by category
7. **Follow the pattern** `<category>_<profile|purpose>_<service|resource>`

## Testing Secrets

After creating secrets in Dashlane, verify they're accessible via CLI:

### 1. Authenticate with Dashlane CLI

```bash
# Configure and authenticate
dcli configure

# Verify authentication
dcli status
```

### 2. Test Secret Retrieval

```bash
# List all secrets (to verify title matches)
dcli password list

# Read a specific SSH key
dcli read ssh_key_personal_github --output raw

# Should output the private key content
# -----BEGIN OPENSSH PRIVATE KEY-----
# ...
# -----END OPENSSH PRIVATE KEY-----
```

### 3. Test in Ansible

Run the validate task for the dashlane_secrets role:

```bash
# Activate Ansible venv
source ~/venv-ansible/bin/activate

# Test dashlane_secrets role validation
ansible-playbook -i localhost, -c local \
  -e "ansible_python_interpreter=/usr/bin/python3" \
  -m include_role -a "name=dashlane_secrets tasks_from=validate" \
  /dev/null
```

### 4. Test SSH Key Deployment

```bash
# Test deploying a specific SSH key
ansible-playbook playbooks/tests/test_ssh_config.yml --tags deploy_keys -v
```

## Troubleshooting

### Secret Not Found

**Error:** `Secret 'ssh_key_personal_github' not found in Dashlane`

**Solutions:**
1. **Check exact title** - Titles are case-sensitive and must match exactly
   ```bash
   dcli password list | grep ssh_key
   ```

2. **Sync vault** - Ensure latest changes are synced
   ```bash
   dcli sync
   ```

3. **Check authentication** - Re-authenticate if needed
   ```bash
   dcli status
   dcli configure  # if needed
   ```

### Permission Denied on SSH Keys

**Error:** SSH keys deployed but authentication fails

**Solutions:**
1. **Check permissions** - Private keys must be 0600
   ```bash
   ls -la ~/.ssh/id_*
   chmod 600 ~/.ssh/id_github
   ```

2. **Verify key format** - Ensure complete key was saved (BEGIN/END markers)
   ```bash
   head -1 ~/.ssh/id_github  # Should show -----BEGIN
   tail -1 ~/.ssh/id_github  # Should show -----END
   ```

3. **Test key manually**
   ```bash
   ssh -i ~/.ssh/id_github -T git@github.com
   ```

### Dashlane CLI Not Authenticated

**Error:** `Dashlane CLI is not authenticated`

**Solutions:**
1. **Run configuration**
   ```bash
   dcli configure
   ```

2. **Follow browser prompts** - You'll be redirected to login via browser

3. **Verify status**
   ```bash
   dcli status
   ```

### Special Characters in Secrets

**Issue:** Secret contains special characters that break shell parsing

**Solution:** Dashlane CLI handles this automatically when using `--output raw`:
```bash
# Correct - uses raw output
dcli read my_secret --output raw

# Incorrect - may have escaping issues
dcli read my_secret
```

The `dashlane_secrets` role always uses `--output raw` to avoid this.

## Reference

### Dashlane CLI Commands

```bash
# Authentication
dcli configure              # Initial setup and authentication
dcli status                 # Check authentication status
dcli sync                   # Sync vault with cloud
dcli logout                 # Logout from current session

# Reading Secrets
dcli read <title> --output raw              # Get full content
dcli read <title> --field username          # Get specific field
dcli read <title> --field password          # Get password only

# Listing Secrets
dcli password list          # List all login items
dcli note list             # List all secure notes

# Creating Secrets (if needed)
dcli note create --title "name" --content "value"
dcli password create --title "name" --login "user" --password "pass"
```

### Ansible Role Documentation

For implementation details, see:
- [dashlane_secrets role README](../roles/dashlane_secrets/README.md)
- [ssh_config role README](../roles/ssh_config/README.md)

### External Resources

- [Dashlane CLI Documentation](https://cli.dashlane.com/)
- [Dashlane CLI GitHub](https://github.com/Dashlane/dashlane-cli)
- [SSH Key Generation Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

## Summary

### Complete Secrets Inventory

**Personal Profile (Minimum Required):**
- `ssh_key_personal_github` - GitHub SSH key

**Work Profile (Minimum Required):**
- `ssh_key_work_gitlab` - Work GitLab SSH key
- `ssh_key_shadowman_git` - Shadowman git SSH key
- `vpn_shadowman_profile` - Shadowman VPN .ovpn file
- `cert_shadowman_root_ca` - Shadowman root CA certificate

**Optional (Both Profiles):**
- `ssh_config_<profile>` - Complete SSH client configuration
- `gitconfig_<profile>` - Complete git configuration
- `zshrc_<profile>` - Complete shell configuration
- `openshift_root_ca` - OpenShift cluster CA certificate

### Key Points

**Format:** All SSH keys, VPN profiles, and certificates are stored as **Secure Notes** with complete file content.

**Naming:** Use exact titles as documented - they are case-sensitive and must match exactly.

**Pattern:** Follow `<category>_<profile|purpose>_<service|resource>` for all new secrets.

**Testing:** Always test with `dcli read <secret_name> --output raw` before running playbooks.

**Search:** Use `dcli note list | grep <prefix>` to find secrets by category.

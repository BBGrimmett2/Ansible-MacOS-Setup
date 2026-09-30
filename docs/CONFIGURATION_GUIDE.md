# Configuration Guide

This guide explains how to configure all secrets, SSH hosts, VPN profiles, and certificates in a centralized, extensible way through `inventories/host_vars/localhost.yml`.

## Table of Contents

- [Overview](#overview)
- [SSH Keys Configuration](#ssh-keys-configuration)
- [SSH Host Configuration](#ssh-host-configuration)
- [VPN Profiles Configuration](#vpn-profiles-configuration)
- [Certificates Configuration](#certificates-configuration)
- [Examples](#examples)

---

## Overview

All configuration is centralized in `inventories/host_vars/localhost.yml`. This file controls:
- Which SSH keys to deploy from Dashlane
- SSH config Host blocks with custom options per environment
- Which VPN profiles to deploy
- Which certificates to install

**Benefits:**
- ✅ Single source of truth for all secrets configuration
- ✅ Enable/disable individual items without code changes
- ✅ Extensible - add new environments by editing config file
- ✅ No hardcoded assumptions in playbooks or roles

---

## SSH Keys Configuration

Define SSH keys to deploy from Dashlane to local filesystem.

**Location:** `inventories/host_vars/localhost.yml`

```yaml
ssh_keys:
  - name: github                           # Friendly name for reference
    dashlane_secret: ssh_key_github        # Secret name in Dashlane
    file: "{{ ssh_directory }}/id_github"  # Deployment path
    host_pattern: "github.com"             # Associated host (for reference)
    enabled: true                          # Deploy this key

  - name: shadowman_git
    dashlane_secret: ssh_key_shadowman_git
    file: "{{ ssh_directory }}/id_shadowman"
    host_pattern: "git.shadowman.dev"
    enabled: true

  - name: starbase_local
    dashlane_secret: ssh_key_starbase_local
    file: "{{ ssh_directory }}/starbase-local"
    host_pattern: "*.local.starbase.icu"
    enabled: false  # Disabled - won't be deployed
```

**Fields:**
- `name` - Friendly identifier (used in logs)
- `dashlane_secret` - Exact title of Dashlane Secure Note containing the private key
- `file` - Full path where SSH key will be deployed (0600 permissions)
- `host_pattern` - Reference to associated hosts (not enforced, just documentation)
- `enabled` - `true` to deploy, `false` to skip

**To add a new SSH key:**
1. Create the private key in Dashlane as a Secure Note
2. Add entry to `ssh_keys` list in `localhost.yml`
3. Set `enabled: true`
4. Run playbook: `ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh`

---

## SSH Host Configuration

Define SSH config file Host blocks with custom options per environment.

**Location:** `inventories/host_vars/localhost.yml`

```yaml
ssh_host_configs:
  - name: github
    host_pattern: "github.com"
    hostname: "github.com"
    user: git
    identity_file: "~/.ssh/id_github"
    options:
      IdentitiesOnly: "yes"
    enabled: true

  - name: shadowman_internal
    host_pattern: "*.shadowman.dev !git.shadowman.dev"  # Wildcard with exclusion
    user: bgrimmet
    identity_file: "~/.ssh/id_shadowman"
    options:
      PreferredAuthentications: publickey
      ForwardAgent: "yes"
    enabled: true

  - name: starbase_local
    host_pattern: "*.local.starbase.icu"
    user: briangrimmett
    identity_file: "~/.ssh/starbase-local"
    options:
      PreferredAuthentications: publickey
    enabled: false

  - name: via_bastion
    host_pattern: "*.internal.example.com"
    user: myuser
    identity_file: "~/.ssh/id_bastion"
    proxy_jump: "bastion.example.com"  # Jump through bastion
    options:
      PreferredAuthentications: publickey
    enabled: false
```

**Fields:**
- `name` - Friendly identifier
- `host_pattern` - SSH Host pattern (supports wildcards, negation with `!`)
- `hostname` - (Optional) Actual hostname to connect to
- `user` - (Optional) SSH username
- `identity_file` - (Optional) Path to SSH private key
- `proxy_jump` - (Optional) Jump/bastion host to proxy through
- `options` - (Optional) Dictionary of additional SSH options
- `enabled` - `true` to include in SSH config, `false` to skip

**Generated SSH Config:**

The template generates:
```ssh-config
# github
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_github
    IdentitiesOnly yes

# starbase_local
Host *.local.starbase.icu
    User briangrimmett
    IdentityFile ~/.ssh/starbase-local
    PreferredAuthentications publickey
```

**Common SSH Options:**

```yaml
options:
  IdentitiesOnly: "yes"           # Only use specified identity file
  ForwardAgent: "yes"             # Forward SSH agent
  PreferredAuthentications: publickey  # Use public key auth only
  ControlMaster: auto             # Multiplexing master
  ControlPath: "~/.ssh/control-%r@%h:%p"  # Control socket path
  ControlPersist: "10m"           # Keep connection alive
  ServerAliveInterval: 60         # Keep-alive interval
  ServerAliveCountMax: 3          # Max keep-alive attempts
  Compression: "yes"              # Enable compression
  Port: 2222                      # Custom SSH port
```

**To add a new SSH host configuration:**
1. Add entry to `ssh_host_configs` list in `localhost.yml`
2. Configure host_pattern, user, identity_file, and any custom options
3. Set `enabled: true`
4. Run playbook: `ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh`
5. Verify: `cat ~/.ssh/config`

---

## VPN Profiles Configuration

Define VPN profiles to deploy from Dashlane to local filesystem.

**Location:** `inventories/host_vars/localhost.yml`

```yaml
vpn_profiles:
  - name: shadowman
    dashlane_secret: vpn_shadowman_profile
    file: "{{ user_home }}/.vpn/shadowman.ovpn"
    enabled: true

  - name: personal_vpn
    dashlane_secret: vpn_personal_profile
    file: "{{ user_home }}/.vpn/personal.ovpn"
    enabled: false

  - name: client_vpn
    dashlane_secret: vpn_client_profile
    file: "{{ user_home }}/.vpn/client.ovpn"
    enabled: false
```

**Fields:**
- `name` - Friendly identifier
- `dashlane_secret` - Exact title of Dashlane Secure Note containing the .ovpn file
- `file` - Full path where VPN profile will be deployed (0600 permissions)
- `enabled` - `true` to deploy, `false` to skip

**To add a new VPN profile:**
1. Store complete .ovpn file in Dashlane as a Secure Note
2. Add entry to `vpn_profiles` list in `localhost.yml`
3. Set `enabled: true`
4. Run playbook: `ansible-playbook playbooks/bootstrap_workstation.yml --tags vpn`
5. Test: `sudo openvpn --config ~/.vpn/name.ovpn`

---

## Certificates Configuration

Define certificates to deploy from Dashlane and install to system keychain.

**Location:** `inventories/host_vars/localhost.yml`

```yaml
certificates:
  - name: shadowman_root_ca
    dashlane_secret: cert_shadowman_root_ca
    file: "{{ user_home }}/.certs/shadowman_root_ca.pem"
    keychain_name: "Shadowman"
    enabled: true

  - name: openshift_root_ca
    dashlane_secret: cert_openshift_root_ca
    file: "{{ user_home }}/.certs/openshift_root_ca.pem"
    keychain_name: "OpenShift"
    enabled: false

  - name: company_root_ca
    dashlane_secret: cert_company_root_ca
    file: "{{ user_home }}/.certs/company_root_ca.pem"
    keychain_name: "Company Root CA"
    enabled: false
```

**Fields:**
- `name` - Friendly identifier
- `dashlane_secret` - Exact title of Dashlane Secure Note containing the PEM certificate
- `file` - Full path where certificate will be deployed (0644 permissions)
- `keychain_name` - Name used when searching system keychain
- `enabled` - `true` to deploy and install, `false` to skip

**To add a new certificate:**
1. Store PEM-encoded certificate in Dashlane as a Secure Note
2. Add entry to `certificates` list in `localhost.yml`
3. Set `enabled: true`
4. Run playbook: `ansible-playbook playbooks/bootstrap_workstation.yml --tags certificates --ask-become-pass`
5. Verify: `security find-certificate -c "Name" /Library/Keychains/System.keychain`

---

## Examples

### Example 1: Add New Environment (Acme Corp)

You need to add SSH access, VPN, and CA certificate for Acme Corp infrastructure.

**1. Generate SSH key:**
```bash
ssh-keygen -t ed25519 -C "you@acme.com" -f ~/.ssh/temp_acme
```

**2. Store secrets in Dashlane:**
```bash
dcli note add --title "ssh_key_acme" --content "$(cat ~/.ssh/temp_acme)"
dcli note add --title "vpn_acme_profile" --content "$(cat /path/to/acme.ovpn)"
dcli note add --title "cert_acme_root_ca" --content "$(cat /path/to/acme-ca.pem)"
rm ~/.ssh/temp_acme*
```

**3. Update `inventories/host_vars/localhost.yml`:**

```yaml
ssh_keys:
  # ... existing keys ...
  - name: acme
    dashlane_secret: ssh_key_acme
    file: "{{ ssh_directory }}/id_acme"
    host_pattern: "*.acme.com"
    enabled: true

ssh_host_configs:
  # ... existing configs ...
  - name: acme_internal
    host_pattern: "*.acme.com"
    user: youruser
    identity_file: "~/.ssh/id_acme"
    options:
      PreferredAuthentications: publickey
      ForwardAgent: "yes"
    enabled: true

vpn_profiles:
  # ... existing profiles ...
  - name: acme
    dashlane_secret: vpn_acme_profile
    file: "{{ user_home }}/.vpn/acme.ovpn"
    enabled: true

certificates:
  # ... existing certs ...
  - name: acme_root_ca
    dashlane_secret: cert_acme_root_ca
    file: "{{ user_home }}/.certs/acme_root_ca.pem"
    keychain_name: "Acme Corp Root CA"
    enabled: true
```

**4. Run playbook:**
```bash
ansible-playbook playbooks/bootstrap_workstation.yml --ask-become-pass
```

**5. Test:**
```bash
# SSH
ssh -T git@git.acme.com

# VPN
sudo openvpn --config ~/.vpn/acme.ovpn

# Certificate
security find-certificate -c "Acme Corp Root CA" /Library/Keychains/System.keychain
```

### Example 2: Bastion/Jump Host Setup

Configure access to internal hosts through a bastion server.

```yaml
ssh_keys:
  - name: bastion
    dashlane_secret: ssh_key_bastion
    file: "{{ ssh_directory }}/id_bastion"
    host_pattern: "bastion.example.com"
    enabled: true

ssh_host_configs:
  # Bastion host with connection multiplexing
  - name: bastion
    host_pattern: "bastion.example.com"
    hostname: "bastion.example.com"
    user: myuser
    identity_file: "~/.ssh/id_bastion"
    options:
      ForwardAgent: "yes"
      ControlMaster: auto
      ControlPath: "~/.ssh/control-%r@%h:%p"
      ControlPersist: "10m"
    enabled: true

  # Internal hosts via bastion
  - name: internal_via_bastion
    host_pattern: "*.internal.example.com"
    user: myuser
    identity_file: "~/.ssh/id_bastion"
    proxy_jump: "bastion.example.com"
    options:
      PreferredAuthentications: publickey
    enabled: true
```

**Usage:**
```bash
# First connection establishes the master
ssh bastion.example.com

# Subsequent connections reuse the master (faster)
ssh server.internal.example.com  # Automatically jumps through bastion
```

### Example 3: Multiple GitHub Accounts

Separate SSH keys for personal and work GitHub accounts.

```yaml
ssh_keys:
  - name: github_personal
    dashlane_secret: ssh_key_github_personal
    file: "{{ ssh_directory }}/id_github_personal"
    host_pattern: "github.com"
    enabled: true

  - name: github_work
    dashlane_secret: ssh_key_github_work
    file: "{{ ssh_directory }}/id_github_work"
    host_pattern: "github.com"
    enabled: true

ssh_host_configs:
  - name: github_personal
    host_pattern: "github.com-personal"
    hostname: "github.com"
    user: git
    identity_file: "~/.ssh/id_github_personal"
    options:
      IdentitiesOnly: "yes"
    enabled: true

  - name: github_work
    host_pattern: "github.com-work"
    hostname: "github.com"
    user: git
    identity_file: "~/.ssh/id_github_work"
    options:
      IdentitiesOnly: "yes"
    enabled: true
```

**Usage:**
```bash
# Personal repos
git clone git@github.com-personal:username/personal-repo.git

# Work repos
git clone git@github.com-work:company/work-repo.git
```

---

## Best Practices

### 1. Secret Naming Convention

Follow the established pattern:
```
<category>_<profile|purpose>_<service|resource>
```

Examples:
- `ssh_key_github`
- `ssh_key_shadowman_git`
- `vpn_shadowman_profile`
- `cert_shadowman_root_ca`

### 2. Enable/Disable Strategy

- Keep all possible configurations in `localhost.yml`
- Use `enabled: false` for unused items
- Easy to enable later without recreating configuration

### 3. Documentation

Add comments in `localhost.yml` for each configuration:

```yaml
ssh_host_configs:
  # Production environment - requires VPN
  - name: prod
    host_pattern: "*.prod.example.com"
    # ... config ...
    enabled: false  # Only enable when working with production
```

### 4. Version Control

- Commit `inventories/host_vars/localhost.yml` to version control
- Secrets are **not** in this file - only Dashlane secret names
- Safe to share with team members

### 5. Testing

Test changes incrementally:
```bash
# Test SSH keys only
ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh_config:keys

# Test SSH config only
ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh_config:config

# Test VPN only
ansible-playbook playbooks/bootstrap_workstation.yml --tags vpn

# Test certificates only
ansible-playbook playbooks/bootstrap_workstation.yml --tags certificates --ask-become-pass
```

---

## Troubleshooting

### Configuration not taking effect

```bash
# Verify configuration syntax
ansible-playbook playbooks/bootstrap_workstation.yml --syntax-check

# Run with verbose output
ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh -vv
```

### SSH config not generated correctly

```bash
# Check enabled hosts
cat inventories/host_vars/localhost.yml | grep -A 10 "ssh_host_configs:"

# Verify template
cat ~/.ssh/config

# Regenerate
ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh_config:config
```

### Secret not found in Dashlane

```bash
# List all Dashlane secrets
dcli note list | sort

# Verify exact name matches
dcli read ssh_key_shadowman_git --output raw | head -1
```

---

## Reference

### Related Documentation

- [DASHLANE_SECRETS_SETUP.md](DASHLANE_SECRETS_SETUP.md) - Dashlane secret creation
- [SHADOWMAN_SETUP.md](SHADOWMAN_SETUP.md) - Shadowman infrastructure guide
- [ssh_config role README](../roles/ssh_config/README.md) - SSH role details
- [network_tools role README](../roles/network_tools/README.md) - VPN/certificate details

### File Locations

- Configuration: `inventories/host_vars/localhost.yml`
- SSH config template: `roles/ssh_config/templates/ssh_config.j2`
- VPN deployment: `roles/network_tools/tasks/deploy_vpn.yml`
- Certificate deployment: `roles/network_tools/tasks/deploy_certificates.yml`

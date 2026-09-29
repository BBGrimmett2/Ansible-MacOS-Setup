# Sensitive Configuration Files in Dashlane

This guide explains how to store sensitive configuration files in Dashlane instead of keeping them in the repository or using templates.

## Why Store Config Files in Dashlane?

Configuration files often contain sensitive information that shouldn't be in a public repository:

- **SSH Config** - Private hostnames, jump hosts, internal endpoints
- **Shell RC files** - API keys, tokens, private environment variables
- **Git Config** - Signing keys, credential helpers, company-specific rewrites
- **VPN Profiles** - OpenVPN configurations with embedded certificates
- **Custom tool configs** - Company-specific settings

Storing these in Dashlane provides:
- ✅ Keep sensitive endpoints private
- ✅ Profile-specific configurations (personal vs work)
- ✅ Easy updates without touching code
- ✅ Backup and sync across devices
- ✅ Secure encryption

## Supported Configuration Files

### 1. SSH Config (~/.ssh/config)

**Dashlane Secret Names:**
- Personal: `ssh_config_personal`
- Work: `ssh_config_work`

**Enable in Ansible:**
```yaml
ssh_config_from_dashlane: true
```

**Use when you need:**
- Private hostnames/endpoints
- Company jump hosts or bastions
- VPN-dependent SSH routes
- Custom SSH options per host

**Example content:**
```ssh-config
# Global settings
Host *
  AddKeysToAgent yes
  UseKeychain yes
  ServerAliveInterval 60

# Company resources via jump host
Host *.company.internal
  ProxyJump bastion.company.com
  User your_username
  IdentityFile ~/.ssh/id_work

# Production database (internal only)
Host prod-db
  HostName db.prod.company.internal
  User dbadmin
  Port 5432
  ProxyJump bastion.company.com
```

### 2. ZSH Config (~/.zshrc)

**Dashlane Secret Names:**
- Personal: `zshrc_personal`
- Work: `zshrc_work`

**Enable in Ansible:**
```yaml
shell_environment_zshrc_from_dashlane: true
```

**Use when you need:**
- API keys as environment variables
- Private tool configurations
- Company-specific aliases/functions
- Sensitive PATH additions

**Example content:**
```bash
# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# Sensitive API Keys
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Company-specific
export COMPANY_REGISTRY="docker.company.internal:5000"
export VAULT_ADDR="https://vault.company.internal"
export VAULT_TOKEN="s.xxxxxxxxxxxxxxxx"

# Internal tools
export PATH="/opt/company/tools:$PATH"
alias vpn-connect='openvpn --config /etc/openvpn/company.ovpn'
alias ssh-prod='ssh -i ~/.ssh/id_prod bastion.company.com'

# FZF with custom config
export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
export FZF_DEFAULT_OPTS='--height 40% --layout=reverse'

# Load completions
source <(kubectl completion zsh)
source <(helm completion zsh)
```

### 3. Git Config (~/.gitconfig)

**Dashlane Secret Names:**
- Personal: `gitconfig_personal`
- Work: `gitconfig_work`

**Enable in Ansible:**
```yaml
development_tools_gitconfig_from_dashlane: true
```

**Use when you need:**
- GPG signing configuration
- Company-specific URL rewrites
- Credential helpers with tokens
- Conditional includes for work repos

**Example content:**
```ini
[user]
	name = Your Name
	email = you@company.com
	signingkey = ABC123DEF456

[core]
	editor = vim
	pager = delta
	autocrlf = input

[commit]
	gpgsign = true

[gpg]
	program = gpg2

# Rewrite company URLs to use SSH
[url "git@gitlab.company.internal:"]
	insteadOf = https://gitlab.company.internal/

# Use credential helper with stored token
[credential "https://github.com"]
	helper = store

# Company-specific settings for work repos
[includeIf "gitdir:~/work/"]
	path = ~/.gitconfig-work

[init]
	defaultBranch = main

[pull]
	rebase = true

[alias]
	st = status
	co = checkout
	br = branch
	ci = commit
	unstage = reset HEAD --
	last = log -1 HEAD
```

## How to Set Up

### Step 1: Export Your Current Config

```bash
# SSH config
cat ~/.ssh/config

# ZSH config
cat ~/.zshrc

# Git config
cat ~/.gitconfig
```

### Step 2: Create Dashlane Secure Note

1. Open Dashlane (web or desktop app)
2. Click **+ Add New** → **Secure Note**
3. **Title:** Use exact name from table above
   - `ssh_config_personal` or `ssh_config_work`
   - `zshrc_personal` or `zshrc_work`
   - `gitconfig_personal` or `gitconfig_work`
4. **Content:** Paste your complete config file
5. Click **Save**
6. Run `dcli sync` to sync changes

### Step 3: Enable in Ansible

Create a file `group_vars/localhost.yml` or update your existing vars:

```yaml
---
# Enable Dashlane config files
ssh_config_from_dashlane: true
shell_environment_zshrc_from_dashlane: true
development_tools_gitconfig_from_dashlane: true
```

Or pass as extra vars when running playbook:

```bash
ansible-playbook playbooks/bootstrap_workstation.yml \
  -e "ssh_config_from_dashlane=true" \
  -e "shell_environment_zshrc_from_dashlane=true" \
  -e "development_tools_gitconfig_from_dashlane=true"
```

### Step 4: Test Retrieval

```bash
# Test Dashlane authentication
dcli status

# Test secret retrieval
dcli read ssh_config_personal --output raw
dcli read zshrc_personal --output raw
dcli read gitconfig_personal --output raw
```

### Step 5: Run Playbook

```bash
source ~/venv-ansible/bin/activate
cd ~/ansible-macos-setup

ansible-playbook playbooks/bootstrap_workstation.yml
```

## Backup Strategy

Before enabling Dashlane deployment, the automation automatically backs up your existing files:

- `~/.ssh/config.backup.<timestamp>`
- `~/.zshrc.backup.<timestamp>`
- `~/.gitconfig.backup.<timestamp>`

You can disable backups if desired:

```yaml
ssh_backup_existing: false
shell_environment_backup_existing: false
development_tools_gitconfig_backup: false
```

## Updating Configs

To update a configuration:

1. **Edit in Dashlane:**
   - Open the secure note in Dashlane
   - Make your changes
   - Save
   - Run `dcli sync`

2. **Re-run Ansible:**
   ```bash
   ansible-playbook playbooks/bootstrap_workstation.yml --tags ssh_config,shell,development
   ```

3. **Or manually test:**
   ```bash
   # Deploy just SSH config
   dcli read ssh_config_personal --output raw > ~/.ssh/config
   chmod 600 ~/.ssh/config
   ```

## Security Best Practices

### Do NOT Store These in Dashlane Notes

❌ **SSH Private Keys** - Use dedicated SSH key secrets instead (e.g., `ssh_key_personal_github`)
❌ **Passwords** - Use Dashlane Login entries, not Secure Notes
❌ **Large binary files** - Dashlane is for text-based configs

### DO Store These in Config Files

✅ Hostnames and endpoints
✅ API keys as environment variables
✅ Tool configurations
✅ Aliases and functions
✅ PATH modifications

### Keep Config Files Clean

```bash
# Good - API key in environment variable
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Good - SSH config with hostname
Host prod-db
  HostName db.company.internal
  User admin

# Bad - Embedding private key directly in config
# (Use ssh_key_* secrets instead)
```

## Template vs Dashlane: When to Use Which

### Use Ansible Templates When:
- ✅ Config is not sensitive
- ✅ Config is generic across users
- ✅ Config needs variable substitution
- ✅ Config is managed in the repo

### Use Dashlane When:
- ✅ Config contains sensitive data
- ✅ Config is user/company-specific
- ✅ Config contains endpoints you don't want public
- ✅ Config contains API keys or tokens

## Troubleshooting

### Config not deploying

**Check Dashlane secret exists:**
```bash
dcli note list | grep ssh_config
dcli note list | grep zshrc
dcli note list | grep gitconfig
```

**Verify exact title match:**
- Must be exact: `ssh_config_personal` not `SSH Config Personal`
- Case-sensitive
- No spaces before/after title

**Check variable is set:**
```bash
# In your playbook, add debug task
- debug:
    msg: "ssh_config_from_dashlane = {{ ssh_config_from_dashlane }}"
```

### Config deployed but not working

**SSH Config Issues:**
```bash
# Test SSH config syntax
ssh -G github.com

# Verbose SSH connection
ssh -v git@github.com
```

**ZSH Config Issues:**
```bash
# Check for syntax errors
zsh -n ~/.zshrc

# Source with debugging
zsh -x ~/.zshrc
```

**Git Config Issues:**
```bash
# Verify git config
git config --list --show-origin

# Test specific setting
git config user.email
```

### Merging Template and Dashlane Configs

If you want both template-generated and Dashlane-stored configs:

**Option 1: Use conditional includes**
```bash
# In your Dashlane zshrc, add at the end:
[ -f ~/.zshrc.local ] && source ~/.zshrc.local
```

Then use Ansible to deploy `.zshrc.local` from template.

**Option 2: Use separate profile files**
```bash
# Dashlane manages main .zshrc
# Ansible manages ~/.zshrc.d/*.zsh includes
```

## Reference

### Default Secret Names

| Config File | Personal Secret | Work Secret |
|------------|----------------|-------------|
| SSH config | `ssh_config_personal` | `ssh_config_work` |
| ZSH config | `zshrc_personal` | `zshrc_work` |
| Git config | `gitconfig_personal` | `gitconfig_work` |

### Variables to Enable

| Feature | Variable | Default |
|---------|----------|---------|
| SSH config from Dashlane | `ssh_config_from_dashlane` | `false` |
| ZSH config from Dashlane | `shell_environment_zshrc_from_dashlane` | `false` |
| Git config from Dashlane | `development_tools_gitconfig_from_dashlane` | `false` |

### Custom Secret Names

Override default secret names if needed:

```yaml
# Personal profile custom names
ssh_config_dashlane_secret_personal: "my_custom_ssh_config"
shell_environment_zshrc_dashlane_secret_personal: "my_custom_zshrc"
development_tools_gitconfig_dashlane_secret_personal: "my_custom_gitconfig"

# Work profile custom names
ssh_config_dashlane_secret_work: "work_ssh_config"
shell_environment_zshrc_dashlane_secret_work: "work_zshrc"
development_tools_gitconfig_dashlane_secret_work: "work_gitconfig"
```

## See Also

- [DASHLANE_SECRETS_SETUP.md](DASHLANE_SECRETS_SETUP.md) - SSH keys and credentials
- [DASHLANE_QUICK_REFERENCE.md](DASHLANE_QUICK_REFERENCE.md) - Quick cheat sheet
- [SSH Config Role README](../roles/ssh_config/README.md) - SSH configuration details
- [Shell Environment Role README](../roles/shell_environment/README.md) - Shell customization
- [Development Tools Role README](../roles/development_tools/README.md) - Git configuration

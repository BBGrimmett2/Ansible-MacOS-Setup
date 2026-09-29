# Ansible Role: ssh_config

Deploy SSH configuration and keys based on workstation profile (personal vs. work).

Fetches SSH keys securely from Dashlane CLI and configures SSH client settings appropriate for each profile.

## Features

- **Profile-aware key deployment** - Different SSH keys for personal vs. work
- **Secure key management** - Keys fetched from Dashlane at runtime (never committed)
- **SSH config templates** - Profile-specific SSH client configuration
- **Known hosts management** - Pre-populate known_hosts for common services
- **macOS Keychain integration** - Add keys to macOS keychain automatically

## Requirements

- macOS
- Dashlane CLI installed and authenticated (`dcli login`)
- SSH keys stored in Dashlane with proper names
- `dashlane_secrets` role (dependency)

## Role Variables

### Profile Selection

```yaml
# Required: Set via vars_prompt in playbook
workstation_profile: personal  # or work
```

### Personal Profile Keys

```yaml
ssh_personal_keys:
  - name: github
    dashlane_secret: ssh_key_personal_github
    file: "{{ ssh_config_dir }}/id_personal_github"
    host_pattern: "github.com"
```

### Work Profile Keys

```yaml
ssh_work_keys:
  - name: work_gitlab
    dashlane_secret: ssh_key_work_gitlab
    file: "{{ ssh_config_dir }}/id_work_gitlab"
    host_pattern: "gitlab.yourcompany.com"

  - name: shadowman_git
    dashlane_secret: ssh_key_shadowman_git
    file: "{{ ssh_config_dir }}/id_shadowman"
    host_pattern: "git.shadowman.dev"
```

### Configuration Options

```yaml
# Deploy SSH config file
ssh_deploy_config: true

# Backup existing config
ssh_backup_existing: true

# Manage known_hosts
ssh_manage_known_hosts: true
ssh_prepopulate_known_hosts: true

# Known hosts to pre-populate
ssh_known_hosts:
  - github.com
  - gitlab.com
```

### SSH Client Options

```yaml
ssh_global_options:
  AddKeysToAgent: "yes"
  UseKeychain: "yes"  # macOS Keychain integration
  IdentitiesOnly: "yes"
  ServerAliveInterval: 60
  ServerAliveCountMax: 3
```

## Dependencies

- `dashlane_secrets` role

## Example Playbook

### Basic Usage (Personal Profile)

```yaml
---
- name: Deploy SSH configuration
  hosts: localhost
  vars_prompt:
    - name: workstation_profile
      prompt: "Workstation profile (personal/work)"
      private: false
      default: personal

  roles:
    - role: ssh_config
```

### Programmatic (Work Profile)

```yaml
---
- name: Deploy work SSH configuration
  hosts: localhost
  roles:
    - role: ssh_config
      vars:
        workstation_profile: work
```

### Custom SSH Keys

```yaml
---
- name: Deploy custom SSH keys
  hosts: localhost
  roles:
    - role: ssh_config
      vars:
        workstation_profile: personal
        ssh_personal_keys:
          - name: github
            dashlane_secret: ssh_key_github
            file: "{{ ansible_env.HOME }}/.ssh/id_github"
            host_pattern: "github.com"

          - name: bitbucket
            dashlane_secret: ssh_key_bitbucket
            file: "{{ ansible_env.HOME }}/.ssh/id_bitbucket"
            host_pattern: "bitbucket.org"
```

## Public Functions

### deploy_personal_keys

Deploy personal SSH keys only.

```yaml
- name: Deploy personal keys
  ansible.builtin.import_role:
    name: ssh_config
    tasks_from: deploy_personal_keys
```

### deploy_work_keys

Deploy work SSH keys only.

```yaml
- name: Deploy work keys
  ansible.builtin.import_role:
    name: ssh_config
    tasks_from: deploy_work_keys
```

### deploy_config

Deploy SSH config file only.

```yaml
- name: Deploy SSH config
  ansible.builtin.import_role:
    name: ssh_config
    tasks_from: deploy_config
  vars:
    workstation_profile: personal
```

### manage_known_hosts

Populate known_hosts file only.

```yaml
- name: Populate known hosts
  ansible.builtin.import_role:
    name: ssh_config
    tasks_from: manage_known_hosts
```

## Dashlane Secret Setup

Before running this role, ensure SSH keys are stored in Dashlane:

### Personal Profile Secrets

Store in Dashlane as "Secure Notes":

- **Title**: `ssh_key_personal_github`
- **Content**: Full SSH private key (including `-----BEGIN OPENSSH PRIVATE KEY-----` headers)

### Work Profile Secrets

- **Title**: `ssh_key_work_gitlab`
- **Content**: Work GitLab SSH private key

- **Title**: `ssh_key_shadowman_git`
- **Content**: Shadowman Git server SSH private key

## Generated SSH Config

### Personal Profile Example

```ssh
# Personal GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_personal_github
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes
```

### Work Profile Example

```ssh
# Work GitLab
Host gitlab.yourcompany.com
    HostName gitlab.yourcompany.com
    User git
    IdentityFile ~/.ssh/id_work_gitlab
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes

# Shadowman Git Server
Host git.shadowman.dev
    HostName git.shadowman.dev
    User git
    IdentityFile ~/.ssh/id_shadowman
    IdentitiesOnly yes
```

## Testing SSH Configuration

### Test SSH Connection

```bash
# Test GitHub connection
ssh -T git@github.com

# Test GitLab connection
ssh -T git@gitlab.yourcompany.com

# Test with verbose output
ssh -Tv git@github.com
```

### Verify Keys in Keychain

```bash
# List keys in ssh-agent
ssh-add -l

# Remove all keys
ssh-add -D

# Re-add with keychain
ssh-add --apple-use-keychain ~/.ssh/id_personal_github
```

### Test Git Operations

```bash
# Clone a repo
git clone git@github.com:username/repo.git

# Check remote URL
cd repo
git remote -v
```

## Troubleshooting

### Permission Denied (publickey)

1. **Verify key is in ssh-agent**:
   ```bash
   ssh-add -l
   ```

2. **Add key manually**:
   ```bash
   ssh-add --apple-use-keychain ~/.ssh/id_personal_github
   ```

3. **Check SSH config**:
   ```bash
   cat ~/.ssh/config
   ```

4. **Test with verbose output**:
   ```bash
   ssh -Tv git@github.com
   ```

### Wrong Key Being Used

1. **Verify IdentitiesOnly**:
   Check `~/.ssh/config` has `IdentitiesOnly yes`

2. **Specify key explicitly**:
   ```bash
   ssh -i ~/.ssh/id_personal_github -T git@github.com
   ```

### Key Not Found in Dashlane

1. **Verify secret name** in Dashlane matches `dashlane_secret` in config
2. **Check Dashlane authentication**:
   ```bash
   dcli whoami
   ```
3. **Test secret retrieval**:
   ```bash
   dcli read ssh_key_personal_github --output raw
   ```

### Keychain Not Persisting

Add this to `~/.ssh/config`:
```ssh
Host *
    AddKeysToAgent yes
    UseKeychain yes
```

Then re-add keys:
```bash
ssh-add --apple-use-keychain ~/.ssh/id_personal_github
```

## Tags

- `ssh_config` - All tasks
- `ssh_config:validate` - Validation only
- `ssh_config:keys` - Key deployment
- `ssh_config:personal` - Personal keys only
- `ssh_config:work` - Work keys only
- `ssh_config:config` - SSH config file
- `ssh_config:known_hosts` - Known hosts management
- `ssh_config:summary` - Display summary

## Security Notes

- SSH keys never committed to git (fetched at runtime from Dashlane)
- Keys stored with restrictive permissions (0600)
- macOS Keychain integration for persistent key storage
- Backup created before overwriting existing config
- IdentitiesOnly prevents key leakage to wrong hosts

## License

MIT

## Author

Brian Grimmett

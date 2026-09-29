## Ansible Role: dashlane_secrets

Securely fetch secrets from Dashlane CLI without hardcoding credentials in your repository.

This role provides public functions to retrieve SSH keys, credentials, and file content from Dashlane at runtime, ensuring no sensitive data is committed to version control.

## Requirements

- macOS (Darwin)
- Dashlane CLI installed (`brew install dashlane-cli`)
- Dashlane CLI authenticated (`dcli login`)
- Active Dashlane account with stored secrets

## Role Variables

### Dashlane CLI Configuration

```yaml
# Dashlane CLI command
dashlane_cli: dcli

# Timeout for Dashlane CLI commands (seconds)
dashlane_timeout: 30
```

### Secret Retrieval Settings

```yaml
# Default permissions for fetched secrets
dashlane_default_permissions: "0600"

# Validate Dashlane authentication before fetching
dashlane_validate_auth: true

# Fail if secret not found (vs. warn and continue)
dashlane_fail_on_missing: true
```

### Logging and Security

```yaml
# Log secret retrieval attempts (names only, not values)
dashlane_log_retrievals: false

# Use no_log for sensitive tasks
dashlane_no_log: true
```

## Dependencies

- Dashlane CLI (installed by install.sh)

## Public Functions

This role exposes three public functions via `tasks_from`:

### 1. fetch_ssh_key

Fetch an SSH private key from Dashlane and save securely.

**Required Variables:**
- `dashlane_secret_name` - Name of the secret in Dashlane
- `dashlane_secret_output_path` - Where to save the SSH key

**Optional Variables:**
- `dashlane_secret_permissions` - File permissions (default: `0600`)

**Example:**

```yaml
- name: Deploy GitHub SSH key
  ansible.builtin.import_role:
    name: dashlane_secrets
    tasks_from: fetch_ssh_key
  vars:
    dashlane_secret_name: "ssh_key_personal_github"
    dashlane_secret_output_path: "{{ ansible_env.HOME }}/.ssh/id_github"
    dashlane_secret_permissions: "0600"
```

### 2. fetch_credential

Fetch username/password credential from Dashlane.

**Required Variables:**
- `dashlane_secret_name` - Name of the credential in Dashlane

**Returns:**
- `dashlane_credential` - Object with `.username` and `.password` properties

**Example:**

```yaml
- name: Fetch service credentials
  ansible.builtin.import_role:
    name: dashlane_secrets
    tasks_from: fetch_credential
  vars:
    dashlane_secret_name: "my_service_login"

- name: Use the credentials
  ansible.builtin.debug:
    msg: "Username: {{ dashlane_credential.username }}"
  # Password available as: {{ dashlane_credential.password }}
```

### 3. fetch_file

Fetch arbitrary file content from Dashlane (certificates, configs, VPN profiles, etc.).

**Required Variables:**
- `dashlane_secret_name` - Name of the file/note in Dashlane
- `dashlane_secret_output_path` - Where to save the file

**Optional Variables:**
- `dashlane_secret_permissions` - File permissions (default: `0600`)

**Example:**

```yaml
- name: Deploy VPN profile
  ansible.builtin.import_role:
    name: dashlane_secrets
    tasks_from: fetch_file
  vars:
    dashlane_secret_name: "vpn_shadowman_profile"
    dashlane_secret_output_path: "{{ ansible_env.HOME }}/.config/vpn/shadowman.ovpn"
    dashlane_secret_permissions: "0600"
```

## Example Playbooks

### Basic Validation Only

```yaml
---
- name: Validate Dashlane CLI
  hosts: localhost
  roles:
    - role: dashlane_secrets
```

### Deploy Multiple SSH Keys

```yaml
---
- name: Deploy SSH Keys
  hosts: localhost
  tasks:
    - name: Deploy GitHub SSH key
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_ssh_key
      vars:
        dashlane_secret_name: "ssh_key_personal_github"
        dashlane_secret_output_path: "{{ ansible_env.HOME }}/.ssh/id_github"

    - name: Deploy Work GitLab SSH key
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_ssh_key
      vars:
        dashlane_secret_name: "ssh_key_work_gitlab"
        dashlane_secret_output_path: "{{ ansible_env.HOME }}/.ssh/id_work_gitlab"

    - name: Deploy Shadowman Git SSH key
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_ssh_key
      vars:
        dashlane_secret_name: "ssh_key_shadowman_git"
        dashlane_secret_output_path: "{{ ansible_env.HOME }}/.ssh/id_shadowman"
```

### Fetch and Use Credentials

```yaml
---
- name: Fetch and Use Service Credentials
  hosts: localhost
  tasks:
    - name: Fetch API credentials from Dashlane
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_credential
      vars:
        dashlane_secret_name: "api_service_credentials"

    - name: Use credentials for API call
      ansible.builtin.uri:
        url: https://api.example.com/endpoint
        user: "{{ dashlane_credential.username }}"
        password: "{{ dashlane_credential.password }}"
        force_basic_auth: true
      no_log: true
```

### Deploy VPN Profiles and Certificates

```yaml
---
- name: Deploy Work VPN Configuration
  hosts: localhost
  tasks:
    - name: Deploy Shadowman VPN profile
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_file
      vars:
        dashlane_secret_name: "vpn_shadowman_profile"
        dashlane_secret_output_path: "/etc/openvpn/shadowman.ovpn"
        dashlane_secret_permissions: "0600"

    - name: Deploy Shadowman root CA
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_file
      vars:
        dashlane_secret_name: "vpn_shadowman_root_ca"
        dashlane_secret_output_path: "/etc/ssl/certs/shadowman-ca.crt"
        dashlane_secret_permissions: "0644"

    - name: Deploy OpenShift root CA
      ansible.builtin.import_role:
        name: dashlane_secrets
        tasks_from: fetch_file
      vars:
        dashlane_secret_name: "openshift_root_ca"
        dashlane_secret_output_path: "/etc/ssl/certs/openshift-ca.crt"
        dashlane_secret_permissions: "0644"
```

## Dashlane Secret Organization

### Recommended Secret Naming Convention

Use descriptive, consistent names for easy identification:

- SSH Keys: `ssh_key_<purpose>_<service>`
  - Examples: `ssh_key_personal_github`, `ssh_key_work_gitlab`, `ssh_key_shadowman_git`

- Credentials: `<service>_credentials` or `<service>_login`
  - Examples: `aws_demo_credentials`, `api_service_login`

- Files: `<type>_<purpose>_<description>`
  - Examples: `vpn_shadowman_profile`, `cert_root_ca`, `config_custom_tool`

### Secret Storage in Dashlane

**For SSH Keys:**
- Store in "Secure Notes"
- Title: Use naming convention (e.g., `ssh_key_personal_github`)
- Content: Paste full SSH private key including headers

**For Credentials:**
- Store in "Passwords"
- Website: Service URL or identifier
- Username: Your username
- Password: Your password
- Title: Use naming convention

**For Files (VPN profiles, certificates, configs):**
- Store in "Secure Notes" or as Attachments
- Title: Use naming convention
- Content: File content as text

## Security Best Practices

1. **Never commit secrets** to git - use this role to fetch at runtime
2. **Use `no_log: true`** when handling secret values in tasks
3. **Set restrictive permissions** (0600) for SSH keys and credentials
4. **Regularly rotate** secrets stored in Dashlane
5. **Limit access** to Dashlane account with MFA enabled
6. **Use separate secrets** for personal vs. work profiles
7. **Audit secret access** through Dashlane's activity log

## Troubleshooting

### Dashlane CLI Not Found

Error: `Dashlane CLI (dcli) is not installed`

**Solution:**
```bash
brew tap dashlane/tap
brew install dashlane-cli
```

### Not Authenticated

Error: `Dashlane CLI is not authenticated`

**Solution:**
```bash
dcli login
```

### Secret Not Found

Error: `Secret 'ssh_key_github' not found in Dashlane`

**Solutions:**
1. Verify secret name spelling in Dashlane
2. Check that you're logged into correct Dashlane account
3. Ensure secret exists in Dashlane vault
4. Set `dashlane_fail_on_missing: false` to warn instead of fail

### Permission Issues

If fetched files have wrong permissions:

```yaml
# Override default permissions
dashlane_secret_permissions: "0644"  # For public files like CAs
# or
dashlane_secret_permissions: "0600"  # For private keys/credentials
```

## Tags

- `dashlane` - All dashlane tasks
- `dashlane:validate` - Validation tasks only
- `dashlane:info` - Display usage information

## License

MIT

## Author

Brian Grimmett

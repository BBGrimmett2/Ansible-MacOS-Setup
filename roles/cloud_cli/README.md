# Cloud CLI Role

Install and configure cloud provider CLI tools with special support for demo environment credential import.

## Overview

This role manages installation of cloud provider command-line tools:

- **AWS CLI** - Amazon Web Services
- **Google Cloud SDK** - Google Cloud Platform (gcloud)
- **Azure CLI** - Microsoft Azure
- **GitHub CLI** - GitHub operations (gh)

## Special Feature: Demo Environment Setup

Quickly import credentials from cloud demo provisioning into new profiles without disrupting existing configurations. Perfect for Red Hat demo environments, training labs, or temporary test accounts.

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

### Installation Control

```yaml
# Install or remove cloud CLIs
cloud_cli_state: present  # or 'absent'

# Install all CLIs (if false, only install enabled CLIs)
cloud_cli_install_all: true
```

### Individual CLI Control

```yaml
cloud_cli_aws_enabled: true
cloud_cli_gcp_enabled: true
cloud_cli_azure_enabled: true
cloud_cli_github_enabled: true
```

### AWS CLI Configuration

```yaml
# Configure AWS CLI
cloud_cli_aws_configure: false

# AWS default region
cloud_cli_aws_default_region: us-east-1

# AWS default output format
cloud_cli_aws_default_output: json
```

### GCP CLI Configuration

```yaml
# Configure GCP CLI
cloud_cli_gcp_configure: false

# GCP default region
cloud_cli_gcp_default_region: us-central1

# GCP default zone
cloud_cli_gcp_default_zone: us-central1-a
```

### Azure CLI Configuration

```yaml
# Configure Azure CLI
cloud_cli_azure_configure: false

# Azure default location
cloud_cli_azure_default_location: eastus

# Azure default output format
cloud_cli_azure_default_output: json
```

### Demo Environment Setup

```yaml
# Enable demo environment helpers
cloud_cli_demo_mode: false

# Demo environment profile name (auto-generated if not set)
cloud_cli_demo_profile_name: "demo-{{ ansible_date_time.date }}"
```

## Dependencies

- `homebrew` role

## Public Functions (tasks_from)

### Installation Functions

```yaml
# Install individual CLIs
- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: install_aws

- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: install_gcp

- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: install_azure

- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: install_github
```

### Demo Configuration Functions

```yaml
# Configure AWS demo environment
- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: configure_aws_demo
  vars:
    aws_demo_account_id: "123456789012"
    aws_demo_region: "us-east-1"
    aws_demo_access_key: "AKIAIOSFODNN7EXAMPLE"
    aws_demo_secret_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    aws_demo_profile_name: "demo-aws-2026"

# Configure GCP demo environment
- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: configure_gcp_demo
  vars:
    gcp_demo_project_id: "my-demo-project"
    gcp_demo_region: "us-central1"
    gcp_demo_credentials_json: "{{ lookup('file', 'service-account.json') }}"
    gcp_demo_config_name: "demo-gcp-2026"

# Configure Azure demo environment
- ansible.builtin.import_role:
    name: cloud_cli
    tasks_from: configure_azure_demo
  vars:
    azure_demo_subscription_id: "12345678-1234-1234-1234-123456789012"
    azure_demo_tenant_id: "87654321-4321-4321-4321-210987654321"
    azure_demo_client_id: "abcdef12-3456-7890-abcd-ef1234567890"
    azure_demo_client_secret: "your-client-secret"
    azure_demo_location: "eastus"
```

## Example Playbook

### Install All Cloud CLIs

```yaml
---
- name: Install cloud CLIs
  hosts: localhost
  roles:
    - role: cloud_cli
```

### Install Specific CLIs Only

```yaml
---
- name: Install AWS and GitHub CLI only
  hosts: localhost
  roles:
    - role: cloud_cli
      vars:
        cloud_cli_install_all: false
        cloud_cli_aws_enabled: true
        cloud_cli_gcp_enabled: false
        cloud_cli_azure_enabled: false
        cloud_cli_github_enabled: true
```

## Demo Environment Workflows

### AWS Demo Environment

When you receive demo AWS credentials:

```bash
# Run the AWS demo setup playbook
ansible-playbook playbooks/setup_aws_demo.yml

# You'll be prompted for:
# - AWS Account ID
# - AWS Region (default: us-east-1)
# - AWS Access Key ID
# - AWS Secret Access Key
# - Profile name (default: demo-YYYY-MM-DD)

# After setup, use the profile:
export AWS_PROFILE=demo-2026-09-29
aws s3 ls
aws ec2 describe-instances
```

### GCP Demo Environment

When you receive demo GCP service account:

```bash
# Run the GCP demo setup playbook
ansible-playbook playbooks/setup_gcp_demo.yml

# You'll be prompted for:
# - GCP Project ID
# - GCP Region (default: us-central1)
# - Service account JSON (paste contents)
# - Configuration name (default: demo-YYYY-MM-DD)

# After setup, activate the configuration:
gcloud config configurations activate demo-2026-09-29
gcloud compute instances list
gcloud storage ls
```

### Azure Demo Environment

When you receive demo Azure service principal:

```bash
# Run the Azure demo setup playbook
ansible-playbook playbooks/setup_azure_demo.yml

# You'll be prompted for:
# - Azure Subscription ID
# - Azure Tenant ID
# - Azure Client ID
# - Azure Client Secret
# - Location (default: eastus)

# After setup, Azure CLI is authenticated:
az vm list
az group list
az account show
```

## Benefits of Demo Environment Functions

1. **Non-Destructive**: Creates new profiles without modifying existing configurations
2. **Quick Setup**: Import credentials in seconds, not minutes of manual configuration
3. **Repeatable**: Run for each new demo environment, keep multiple profiles
4. **Secure**: Credentials stored in standard CLI config locations with proper permissions
5. **Organized**: Auto-generated profile names include dates for easy tracking

## Tags

- `validate` - Run validation tasks only
- `install` - Run installation tasks only

## Testing

### Syntax Check

```bash
ansible-playbook --syntax-check playbooks/tests/test_cloud_cli.yml
```

### Dry Run

```bash
ansible-playbook --check playbooks/tests/test_cloud_cli.yml
```

### Execute

```bash
ansible-playbook playbooks/tests/test_cloud_cli.yml
```

## Post-Installation

### AWS CLI

```bash
# Verify installation
aws --version

# List configured profiles
aws configure list-profiles

# Test connection
aws sts get-caller-identity
```

### GCP CLI

```bash
# Verify installation
gcloud version

# List configurations
gcloud config configurations list

# Test connection
gcloud projects list
```

### Azure CLI

```bash
# Verify installation
az version

# Show current account
az account show

# Test connection
az group list
```

### GitHub CLI

```bash
# Verify installation
gh --version

# Authenticate (interactive)
gh auth login

# Test connection
gh repo list
```

## License

MIT

## Author

Brian Grimmett

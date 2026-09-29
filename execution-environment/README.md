# Execution Environment

This directory contains the definition for building an Ansible Execution Environment (EE) using `ansible-builder`.

## Contents

- `execution-environment.yml` - Main EE definition file
- `requirements.yml` - Ansible Galaxy collections/roles (symlinked from `../collections/requirements.yml`)
- `requirements/` - Additional dependency files
  - `requirements.txt` - Python packages
  - `bindep.txt` - System packages

## Building Locally

To build the execution environment locally:

```bash
cd execution-environment
ansible-builder build --tag my-ee:latest --verbosity 3
```

## Automated Builds (GitHub Actions)

This repository includes a GitHub Actions workflow that automatically builds the execution environment weekly.

### Setup Instructions

1. **Add Registry Secrets**

   Go to your GitHub repository settings: `Settings → Secrets and variables → Actions`

   Add the following repository secrets:

   **Source Registry (where base images are pulled from):**
   - `SOURCE_REGISTRY` - Source registry URL (e.g., `registry.redhat.io`)
   - `SOURCE_REGISTRY_USERNAME` - Your source registry username
   - `SOURCE_REGISTRY_PASSWORD` - Your source registry password or token

   **Destination Registry (where built images are pushed):**
   - `DEST_REGISTRY` - Destination registry URL (e.g., `quay.io`, `ghcr.io`)
   - `DEST_REGISTRY_USERNAME` - Your destination registry username
   - `DEST_REGISTRY_PASSWORD` - Your destination registry password or token

   **Example for Red Hat Registry → Quay.io:**
   - `SOURCE_REGISTRY` = `registry.redhat.io`
   - `SOURCE_REGISTRY_USERNAME` = Your Red Hat username
   - `SOURCE_REGISTRY_PASSWORD` = Your Red Hat registry token
   - `DEST_REGISTRY` = `quay.io`
   - `DEST_REGISTRY_USERNAME` = Your Quay.io username
   - `DEST_REGISTRY_PASSWORD` = Robot account token from [https://quay.io/user/](https://quay.io/user/)

   **Note:** The image name will automatically use your GitHub repository name (e.g., `Megalith-Development/Ansible-Template-Repo`)

3. **Trigger the Workflow**

   The workflow runs:
   - **Automatically:** Every Sunday at 2 AM UTC
   - **On Pull Requests:** When a PR is opened/updated targeting the `main` branch
   - **Manually:** Go to `Actions → Build Execution Environment → Run workflow`

### Image Tags

Built images are tagged with:
- `latest` - Always points to the most recent build
- `YYYYMMDD-HHMMSS` - Timestamp-based tag for each build (UTC)
- Custom tag - Optional tag when manually triggering

## Customization

See the comments in `execution-environment.yml` for examples of:
- Alternative base images
- Custom build steps
- Python and system dependencies
- Build arguments and proxy settings

## Documentation

- [ansible-builder documentation](https://docs.ansible.com/projects/builder/)
- [Execution Environment definition](https://docs.ansible.com/projects/builder/en/latest/definition/)

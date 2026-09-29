# Kubernetes Tools Role

Install and configure Kubernetes and OpenShift tooling for macOS.

## Overview

This role manages installation of essential Kubernetes and OpenShift tools:

- **oc** - OpenShift CLI for Red Hat OpenShift
- **kubectl** - Kubernetes CLI for cluster management
- **helm** - Kubernetes package manager
- **k9s** - Terminal UI for Kubernetes
- **kubectx/kubens** - Quick context and namespace switching
- **stern** - Multi-pod log tailing
- **kustomize** - Kubernetes native configuration management

## Requirements

- macOS
- Homebrew (installed by `homebrew` role)

## Role Variables

### Installation Control

```yaml
# Install or remove Kubernetes tools
kubernetes_tools_state: present  # or 'absent'

# Install all tools (if false, only install enabled tools)
kubernetes_tools_install_all: true
```

### Individual Tool Control

```yaml
kubernetes_tools_oc_enabled: true
kubernetes_tools_kubectl_enabled: true
kubernetes_tools_helm_enabled: true
kubernetes_tools_k9s_enabled: true
kubernetes_tools_kubectx_enabled: true
kubernetes_tools_stern_enabled: true
kubernetes_tools_kustomize_enabled: true
```

### Configuration

```yaml
# Configure kubectl/oc completion
kubernetes_tools_configure_completion: true

# Configure k9s
kubernetes_tools_k9s_configure: false

# k9s configuration directory
kubernetes_tools_k9s_config_dir: "{{ ansible_env.HOME }}/.config/k9s"

# k9s skin/theme
kubernetes_tools_k9s_skin: "nord"
```

## Dependencies

- `homebrew` role

## Public Functions (tasks_from)

```yaml
# Install individual tools
- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_oc

- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_kubectl

- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_helm

- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_k9s

- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_kubectx

- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_stern

- ansible.builtin.import_role:
    name: kubernetes_tools
    tasks_from: install_kustomize
```

## Example Playbook

### Install All Tools

```yaml
---
- name: Install Kubernetes tools
  hosts: localhost
  roles:
    - role: kubernetes_tools
```

### Install Specific Tools Only

```yaml
---
- name: Install OpenShift and K9s only
  hosts: localhost
  roles:
    - role: kubernetes_tools
      vars:
        kubernetes_tools_install_all: false
        kubernetes_tools_oc_enabled: true
        kubernetes_tools_kubectl_enabled: false
        kubernetes_tools_helm_enabled: false
        kubernetes_tools_k9s_enabled: true
        kubernetes_tools_kubectx_enabled: false
        kubernetes_tools_stern_enabled: false
        kubernetes_tools_kustomize_enabled: false
```

### Remove All Tools

```yaml
---
- name: Remove Kubernetes tools
  hosts: localhost
  roles:
    - role: kubernetes_tools
      vars:
        kubernetes_tools_state: absent
```

## Tool Usage

### OpenShift CLI (oc)

```bash
# Login to OpenShift cluster
oc login https://api.cluster.example.com:6443

# Get current project
oc project

# List pods
oc get pods

# View logs
oc logs pod-name

# Port forward
oc port-forward pod-name 8080:8080
```

### Kubernetes CLI (kubectl)

```bash
# Get cluster info
kubectl cluster-info

# List namespaces
kubectl get namespaces

# List pods in all namespaces
kubectl get pods --all-namespaces

# Describe pod
kubectl describe pod pod-name

# Execute command in pod
kubectl exec -it pod-name -- /bin/bash
```

### Helm

```bash
# Add repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Search charts
helm search repo wordpress

# Install chart
helm install my-wordpress bitnami/wordpress

# List releases
helm list

# Uninstall release
helm uninstall my-wordpress
```

### K9s

```bash
# Launch K9s
k9s

# K9s with specific namespace
k9s -n default

# Keyboard shortcuts:
# 0-9: Navigate to different resources
# /: Search
# d: Describe
# l: Logs
# ?: Help
```

### kubectx / kubens

```bash
# List contexts
kubectx

# Switch context
kubectx minikube

# List namespaces
kubens

# Switch namespace
kubens kube-system

# Quick switch to previous context
kubectx -

# Quick switch to previous namespace
kubens -
```

### stern

```bash
# Tail logs from all pods in namespace
stern . -n default

# Tail logs from specific pods
stern pod-name

# Include only certain containers
stern pod-name -c container-name

# Colored output with timestamps
stern pod-name --color always --timestamps
```

### kustomize

```bash
# Build kustomization
kustomize build .

# Apply kustomization
kustomize build . | kubectl apply -f -

# Create kustomization.yaml
kustomize create --autodetect

# Edit images in kustomization
kustomize edit set image nginx=nginx:1.21
```

## Common Workflows

### OpenShift Cluster Access

```bash
# Login to OpenShift
oc login https://api.cluster.openshift.com:6443 --token=your-token

# List all projects
oc projects

# Switch project
oc project my-project

# Create new app
oc new-app https://github.com/openshift/ruby-hello-world

# Expose service
oc expose svc/ruby-hello-world
```

### Kubernetes Development

```bash
# Set context and namespace
kubectx dev-cluster
kubens development

# Deploy application
kubectl apply -f deployment.yaml

# Watch deployment rollout
kubectl rollout status deployment/my-app

# View logs with stern
stern my-app

# Port forward for local testing
kubectl port-forward deployment/my-app 8080:8080
```

### Helm Chart Management

```bash
# Create new chart
helm create my-chart

# Install with custom values
helm install my-release my-chart -f custom-values.yaml

# Upgrade release
helm upgrade my-release my-chart

# Rollback release
helm rollback my-release 1

# View release history
helm history my-release
```

## Tags

- `validate` - Run validation tasks only
- `install` - Run installation tasks only

## Testing

### Syntax Check

```bash
ansible-playbook --syntax-check playbooks/tests/test_kubernetes_tools.yml
```

### Dry Run

```bash
ansible-playbook --check playbooks/tests/test_kubernetes_tools.yml
```

### Execute

```bash
ansible-playbook playbooks/tests/test_kubernetes_tools.yml
```

## Post-Installation

### Verify Installation

```bash
# Check tool versions
oc version
kubectl version --client
helm version
k9s version
kubectx --version
stern --version
kustomize version
```

### Configure Shell Completion

Add to your `~/.zshrc`:

```bash
# kubectl completion
source <(kubectl completion zsh)

# oc completion (OpenShift)
source <(oc completion zsh)

# helm completion
source <(helm completion zsh)
```

### Set Up Aliases

```bash
# Add to ~/.zshrc
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgn='kubectl get nodes'
alias kctx='kubectx'
alias kns='kubens'
```

## Red Hat OpenShift Tips

### Connect to OpenShift Cluster

1. Login to OpenShift web console
2. Click your username → Copy login command
3. Paste token in terminal:
   ```bash
   oc login --token=sha256~xxx --server=https://api.cluster.com:6443
   ```

### Common OpenShift Commands

```bash
# Get cluster version
oc get clusterversion

# Get cluster operators
oc get clusteroperators

# Get nodes
oc get nodes

# Create new project
oc new-project my-project

# Grant admin access
oc adm policy add-role-to-user admin username -n my-project
```

## License

MIT

## Author

Brian Grimmett

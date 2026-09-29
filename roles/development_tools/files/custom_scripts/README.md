# Custom Shell Scripts

This directory contains custom shell commands that are installed to `~/.local/bin` for enhanced productivity.

## Available Scripts

### rhdps
**Red Hat Demo Platform Services Helper**

Quick setup of cloud demo environments with direnv integration.

**Commands:**
- `rhdps setup aws` - Setup AWS demo environment
- `rhdps setup gcp` - Setup GCP demo environment
- `rhdps setup azure` - Setup Azure demo environment
- `rhdps list` - Show current directory environment
- `rhdps clean` - Remove .envrc from current directory
- `rhdps help` - Full help

**Workflow:**
```bash
cd ~/Documents/Projects/demo-aws-project
rhdps setup aws
direnv allow
# Environment auto-loads when entering this directory
```

## Adding Custom Scripts

To add your own custom shell scripts:

1. **Create script** in this directory
2. **Make it executable**: `chmod +x your-script`
3. **Add installation task** in `roles/development_tools/tasks/install_custom_scripts.yml`

### Example: Adding a new script

**1. Create script:** `custom_scripts/mycommand`
```bash
#!/bin/bash
echo "My custom command"
```

**2. Add to install_custom_scripts.yml:**
```yaml
- name: Install mycommand script
  ansible.builtin.copy:
    src: custom_scripts/mycommand
    dest: "{{ ansible_env.HOME }}/.local/bin/mycommand"
    mode: "0755"
```

**3. Test:**
```bash
ansible-playbook playbooks/install_development_tools.yml --tags custom_scripts
mycommand
```

## Script Naming Conventions

- Use lowercase, hyphen-separated names (e.g., `my-command`)
- Avoid conflicts with system commands (`ls`, `cd`, etc.)
- Prefix with project/org for clarity (`rh-`, `demo-`, etc.)

## Integration with Roles

Custom scripts are installed via the `development_tools` role:

```yaml
- ansible.builtin.import_role:
    name: development_tools
    tasks_from: install_custom_scripts
```

Or install individual scripts:

```yaml
- ansible.builtin.import_role:
    name: development_tools
    tasks_from: install_rhdps
```

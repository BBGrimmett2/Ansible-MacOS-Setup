# Ansible Template Repo (WIP)

[![Contribute](https://www.eclipse.org/che/contribute.svg)](https://devspaces.apps.ocp.shadowman.dev/#https://github.com/Megalith-Development/Ansible-Template-Repo)

**Status: In Development**  
This repository is a working template for building and standardizing Ansible projects.

---

## Purpose

Provide a reusable starting point for:
- Ansible playbooks
- Roles and collections
- Inventory structure
- CI/CD integration
- Development workflows

This repo is intended to evolve into a **golden path** for consistent Ansible development.

---

## Structure (WIP)

```
.
├── inventories/        # Inventory definitions (dev, prod, etc.)
├── group_vars/         # Group-level variables
├── host_vars/          # Host-specific variables
├── roles/              # Reusable roles
├── playbooks/          # Playbooks to execute automation
├── .github/workflows/  # CI pipelines (linting, testing)
├── ansible.cfg         # Ansible configuration
├── requirements.yml    # Galaxy collections/roles
└── README.md
```

---

## Getting Started

Clone the repo:

```bash
git clone https://github.com/Megalith-Development/Ansible-Template-Repo.git
cd Ansible-Template-Repo
```

Install dependencies:

```bash
ansible-galaxy install -r requirements.yml
```

Run a playbook:

```bash
ansible-playbook -i inventories/dev/hosts playbooks/example.yml
```

---

## Development Goals

- [ ] Standardized repo structure
- [ ] CI with linting (ansible-lint, yamllint, molecule)
- [ ] Example roles and playbooks
- [ ] Integration with AAP
- [ ] Execution Environment support
- [ ] Documentation improvements
- [ ] Virtualization test servers via DevFile
- [ ] Group Var support with playbooks/ dir

---

## CI / Quality (Planned)

- Ansible Lint
- YAML Lint
- GitHub Actions validation
- Syntax checks for playbooks

---

## Contributing

Contributions welcome (once structure stabilizes).

For now:
- Open issues for ideas
- Submit PRs for improvements

---

## Notes

This is a living template — expect frequent changes as patterns are refined.

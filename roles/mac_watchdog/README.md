# mac_watchdog

An opt-in, user-scoped LaunchAgent deployment of the pinned watchdog
Python package. **Personal Mac only**, never work profile. No root privileges
and no automatic Ansible remediation.

Run:

```sh
ansible-playbook playbooks/install_mac_watchdog.yml -e workstation_profile=personal
```

Requirements: macOS GUI login session, git, Homebrew Python >=3.11
at `/opt/homebrew/bin/python3` (or override `mac_watchdog_python_executable`).
Installation runs as the login user and writes into
`~/.local/share/mac-watchdog`; database history is written by the package
under `~/.local/state/mac-watchdog`.

`mac_watchdog_revision` is pinned to a reviewed watchdog commit and must
be updated by PR. The selected SHA is not automatically changed by upstream
main branch updates.

The launchd agent runs the `monitor` subcommand, which currently performs
metadata-only inventory and 30-minute reconciliation with selected filesystem
events. Weekly deep scanning and Ansible manifest comparison are future
engine work. This role does not silently modify the master bootstrap.

**Not tested on the personal Mac yet.** Use `launchctl print
gui/$(id -u)/icu.starbase.mac-watchdog` to inspect registration after
installation. Never post stdout/stderr or exported inventories publicly.

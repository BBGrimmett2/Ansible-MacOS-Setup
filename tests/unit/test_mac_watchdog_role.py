"""Offline safety and plist-template checks for the personal watchdog deployment."""
from __future__ import annotations

import plistlib
import unittest
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[2]
ROLE = ROOT / "roles" / "mac_watchdog"


class WatchdogRoleTests(unittest.TestCase):
    def test_role_contracts_parse(self) -> None:
        for relative in (
            "defaults/main.yml",
            "meta/argument_specs.yml",
            "tasks/main.yml",
            "tasks/validate.yml",
            "tasks/install.yml",
        ):
            doc = yaml.safe_load((ROLE / relative).read_text())
            self.assertIsNotNone(doc, relative)

    def test_installation_is_pinned_and_opt_in(self) -> None:
        defaults = yaml.safe_load((ROLE / "defaults/main.yml").read_text())
        revision = defaults["mac_watchdog_revision"]
        self.assertRegex(revision, r"^[0-9a-f]{40}$")
        self.assertEqual(
            defaults["mac_watchdog_repo"],
            "https://github.com/BBGrimmett2/MacOS-Config-Watchdog.git",
        )
        playbook = yaml.safe_load(
            (ROOT / "playbooks/install_mac_watchdog.yml").read_text()
        )
        self.assertEqual(playbook[0]["vars"]["workstation_profile"], "personal")
        self.assertEqual(playbook[0]["tasks"][0]["ansible.builtin.import_role"]["name"], "mac_watchdog")

    def test_plist_renders_and_is_user_scoped(self) -> None:
        template = (ROLE / "templates/mac-watchdog.plist.j2").read_text()
        rendered = Environment(undefined=StrictUndefined).from_string(template).render(
            mac_watchdog_launchagent_label="icu.starbase.mac-watchdog",
            mac_watchdog_venv_dir="/Users/test/.local/share/mac-watchdog/venv",
            mac_watchdog_install_root="/Users/test/.local/share/mac-watchdog",
        )
        plist = plistlib.loads(rendered.encode())
        self.assertTrue(plist["RunAtLoad"])
        self.assertTrue(plist["KeepAlive"])
        self.assertEqual(plist["ProgramArguments"][-1], "monitor")
        self.assertNotIn("UserName", plist)
        self.assertNotIn("StartCalendarInterval", plist)

    def test_validation_rejects_nonpersonal_and_unpinned(self) -> None:
        tasks = yaml.safe_load((ROLE / "tasks/validate.yml").read_text())
        checks = tasks[0]["ansible.builtin.assert"]["that"]
        self.assertTrue(any("workstation_profile" in x and "personal" in x for x in checks))
        self.assertTrue(any("mac_watchdog_revision" in x and "40" in x for x in checks))

    def test_no_configuration_writes_through_model(self) -> None:
        text = (ROLE / "tasks/install.yml").read_text()
        # It may install the agent, but must never run the AI or apply a playbook.
        self.assertNotIn("ansible-playbook", text)
        self.assertNotIn("ollama", text)


if __name__ == "__main__":
    unittest.main()

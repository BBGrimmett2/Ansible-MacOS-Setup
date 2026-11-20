"""Static regression tests for Podman CLI and VM Ansible configuration."""
import importlib.util
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class PodmanConfigurationTests(unittest.TestCase):
    def test_installation_and_machine_are_configurable(self):
        defaults = yaml.safe_load((ROOT / "roles/database_tools/defaults/main.yml").read_text())
        self.assertEqual(defaults["database_tools_packages"]["podman"], "podman")
        self.assertEqual(defaults["database_tools_packages"]["podman_desktop"], "podman-desktop")
        self.assertTrue(defaults["database_tools_podman_enabled"])
        self.assertTrue(defaults["database_tools_podman_machine_enabled"])
        self.assertEqual(defaults["database_tools_podman_machine_name"], "podman-machine-default")
        entry = yaml.safe_load((ROOT / "roles/database_tools/tasks/install.yml").read_text())
        self.assertTrue(any(task.get("ansible.builtin.include_tasks") == "install_podman.yml" for task in entry))

    def test_machine_state_checks_guard_mutations(self):
        tasks = yaml.safe_load((ROOT / "roles/database_tools/tasks/install_podman.yml").read_text())
        self.assertEqual(tasks[0]["community.general.homebrew"]["state"], "present")
        commands = [task for task in tasks if "ansible.builtin.command" in task]
        self.assertTrue(any("init" in task["ansible.builtin.command"]["argv"] for task in commands))
        self.assertTrue(any("start" in task["ansible.builtin.command"]["argv"] for task in commands))
        for task in commands:
            if "init" in task["ansible.builtin.command"]["argv"] or "start" in task["ansible.builtin.command"]["argv"]:
                self.assertIn("not ansible_check_mode", task["when"])
                self.assertEqual(task["changed_when"], True)
        self.assertIn("map(attribute='Name')", str(tasks))
        self.assertIn("selectattr('Running'", str(tasks))

    def test_homebrew_manifest_derives_podman(self):
        path = ROOT / "filter_plugins/watchdog_manifest.py"
        spec = importlib.util.spec_from_file_location("watchdog_manifest_podman", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        selection = module.watchdog_role_packages(ROOT)
        self.assertIn("podman", selection["brew_formula"])
        self.assertIn("podman-desktop", selection["brew_cask"])


if __name__ == "__main__":
    unittest.main()

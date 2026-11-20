"""Unit coverage for personal expected-state manifest generation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "filter_plugins" / "watchdog_manifest.py"
spec = importlib.util.spec_from_file_location("watchdog_manifest", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
build = module.watchdog_manifest


class ExpectedStateManifestTests(unittest.TestCase):
    def test_packages_share_original_source_of_truth(self):
        common = yaml.safe_load((ROOT / "inventories/group_vars/all.yml").read_text())[
            "cli_tools_packages_common"
        ]
        personal = yaml.safe_load(
            (ROOT / "inventories/group_vars/profiles/personal.yml").read_text()
        )
        manifest = build(common, personal["cli_tools_packages_extra"],
                         personal["mac_watchdog_expected_resources"])
        assert manifest["schema_version"] == 1
        assert manifest["managed_categories"] == ["brew_formula"]
        assert {x["resource_id"] for x in manifest["resources"]} == {
            "brew_formula:" + name for name in common
        }
        assert json.loads(json.dumps(manifest)) == manifest

    def test_additional_managed_categories_are_explicit(self):
        manifest = build(["git", "git"], [], [
            {"resource_id": "brew_cask:visual-studio-code", "category": "brew_cask"},
            {"resource_id": "app:com.example.editor", "category": "app",
             "attributes": {"version": "2"}}
        ])
        assert manifest["managed_categories"] == ["app", "brew_cask", "brew_formula"]
        assert len(manifest["resources"]) == 3

    def test_conflicting_entries_rejected(self):
        with self.assertRaises(ValueError):
            build(["git"], [], [
                {"resource_id": "brew_formula:git", "category": "brew_formula",
                 "attributes": {"installed": False}}
            ])

    def test_bad_resource_input_rejected(self):
        for item in (
            {"resource_id": "app:com.example", "category": "brew_cask"},
            {"resource_id": "brew_cask:x", "category": "brew_cask",
             "attributes": {"secret": ["not-allowed"]}},
            {"resource_id": "launchd:user_agent:x", "category": "unknown"}
        ):
            with self.subTest(item=item), self.assertRaises(ValueError):
                build([], [], [item])


    def test_role_defaults_expand_formula_and_cask_coverage(self):
        role_names = ("cloud_cli", "kubernetes_tools", "network_tools",
                      "development_tools", "desktop_apps", "database_tools", "terminal")
        defaults = {
            role: yaml.safe_load((ROOT / "roles" / role / "defaults/main.yml").read_text())
            for role in role_names
        }
        profile = yaml.safe_load(
            (ROOT / "inventories/group_vars/profiles/personal.yml").read_text()
        )
        selected = module.watchdog_role_packages(ROOT, profile)
        self.assertIn("awscli", selected["brew_formula"])
        self.assertIn("gh", selected["brew_formula"])
        self.assertIn("helm", selected["brew_formula"])
        self.assertIn("kubernetes-cli", selected["brew_formula"])
        self.assertIn("node", selected["brew_formula"])
        self.assertIn("podman", selected["brew_formula"])
        self.assertIn("openvpn", selected["brew_formula"])
        self.assertIn("wireshark-app", selected["brew_cask"])
        self.assertIn("google-chrome", selected["brew_cask"])
        self.assertIn("gcloud-cli", selected["brew_cask"])
        self.assertIn("wireshark-app", selected["brew_cask"])
        self.assertNotIn("google-cloud-sdk", selected["brew_cask"])
        self.assertNotIn("wireshark", selected["brew_cask"])
        self.assertIn("claude", selected["brew_cask"])
        self.assertIn("font-meslo-lg-nerd-font", selected["brew_cask"])
        self.assertNotIn("cursor", selected["brew_cask"])
        self.assertNotIn("ghostty", selected["brew_cask"])
        self.assertNotIn("nmap", selected["brew_formula"])
        final = build(["bat"], [], [], selected)
        self.assertIn("brew_cask", final["managed_categories"])
        ids = {r["resource_id"] for r in final["resources"]}
        self.assertIn("brew_formula:awscli", ids)
        self.assertIn("brew_cask:google-chrome", ids)

    def test_enabled_flags_respect_personal_overrides(self):
        role_names = ("cloud_cli", "kubernetes_tools", "network_tools",
                      "development_tools", "desktop_apps", "database_tools", "terminal")
        defaults = {
            role: yaml.safe_load((ROOT / "roles" / role / "defaults/main.yml").read_text())
            for role in role_names
        }
        profile = {"network_tools_openvpn_enabled": False,
                   "desktop_apps_discord_enabled": False}
        selected = module.watchdog_role_packages(ROOT, profile)
        self.assertNotIn("openvpn", selected["brew_formula"])
        self.assertNotIn("discord", selected["brew_cask"])
        profile["cloud_cli_state"] = "absent"
        selected = module.watchdog_role_packages(ROOT, profile)
        self.assertNotIn("awscli", selected["brew_formula"])

    def test_role_contract_and_profile_isolation(self):
        role = ROOT / "roles/mac_watchdog_manifest"
        for filename in ("defaults/main.yml", "meta/argument_specs.yml",
                         "tasks/main.yml", "tasks/generate.yml", "tasks/validate.yml"):
            self.assertIsNotNone(yaml.safe_load((role / filename).read_text()))
        playbook = yaml.safe_load(
            (ROOT / "playbooks/export_mac_watchdog_manifest.yml").read_text()
        )[0]
        assert playbook["vars"]["workstation_profile"] == "personal"
        assert "profiles/personal.yml" in str(playbook["pre_tasks"])
        assert "profiles/work.yml" not in str(playbook)
        assert "workstation_profile" in (role / "tasks/validate.yml").read_text()
        assert "mode: '0600'" in (role / "tasks/generate.yml").read_text()
        assert "mode: '0700'" in (role / "tasks/generate.yml").read_text()


if __name__ == "__main__":
    unittest.main()

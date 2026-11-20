"""Profile-specific and idempotent Ollama integration checks."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]


class OllamaSetupTests(unittest.TestCase):
    def test_personal_only_and_canonical_cask(self):
        defaults = yaml.safe_load((ROOT / "roles/desktop_apps/defaults/main.yml").read_text())
        personal = yaml.safe_load((ROOT / "inventories/group_vars/profiles/personal.yml").read_text())
        install = yaml.safe_load((ROOT / "roles/desktop_apps/tasks/install.yml").read_text())
        assert defaults["desktop_apps_packages"]["ollama"] == "ollama-app"
        assert defaults["desktop_apps_ollama_enabled"] is False
        assert personal["desktop_apps_ollama_enabled"] is True
        entry = next(item for item in install if item["ansible.builtin.include_tasks"] == "install_ollama.yml")
        assert "workstation_profile == 'personal'" in entry["when"]

    def test_launch_is_conditional_and_never_approves_security_prompts(self):
        tasks = yaml.safe_load((ROOT / "roles/desktop_apps/tasks/install_ollama.yml").read_text())
        cask, api, open_task, wait_task, pull_task = tasks
        assert cask["community.general.homebrew_cask"]["state"] == "present"
        assert api["changed_when"] is False
        assert api["failed_when"] is False
        assert api["ansible.builtin.uri"]["url"] == "http://127.0.0.1:11434/api/tags"
        assert open_task["ansible.builtin.command"]["argv"] == ["/usr/bin/open", "-a", "Ollama"]
        assert "not ansible_check_mode" in open_task["when"]
        assert any("desktop_apps_ollama_api.status" in x for x in open_task["when"])
        assert pull_task["ansible.builtin.command"]["argv"][1] == "pull"
        assert "not ansible_check_mode" in pull_task["when"]
        assert wait_task["changed_when"] is False
        assert "sudo" not in str(tasks)


if __name__ == "__main__":
    unittest.main()

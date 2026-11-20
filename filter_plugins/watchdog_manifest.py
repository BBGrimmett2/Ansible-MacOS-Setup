"""Build the watchdog's strict JSON contract from non-secret Ansible variables."""
from __future__ import annotations

from pathlib import Path
import yaml


def watchdog_manifest(common, extra, resources, selected=None):
    if not all(isinstance(values, list) for values in (common, extra, resources)):
        raise ValueError("Expected-state package and resource inputs must be lists")
    selected = selected if selected is not None else {"brew_formula": [], "brew_cask": []}
    if not isinstance(selected, dict) or set(selected) not in (\n        frozenset({"brew_formula", "brew_cask"}),\n        frozenset({"brew_formula", "brew_cask", "ollama_model"}),\n    ):
        raise ValueError("Invalid selected package groups")
    if not all(isinstance(selected[group], list) for group in selected):
        raise ValueError("Selected packages must be lists")
    entries = {}
    for name in common + extra + selected["brew_formula"]:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("Invalid Homebrew formula name")
        rid = "brew_formula:" + name
        entries[rid] = {"resource_id": rid, "category": "brew_formula"}
    for name in selected["ollama_model"] if "ollama_model" in selected else []:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("Invalid Ollama model name")
        rid = "ollama_model:" + name
        entries[rid] = {"resource_id": rid, "category": "ollama_model"}
    for name in selected["brew_cask"]:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("Invalid Homebrew cask name")
        rid = "brew_cask:" + name
        entries[rid] = {"resource_id": rid, "category": "brew_cask"}
    for item in resources:
        if not isinstance(item, dict) or set(item) not in (
            {"resource_id", "category"}, {"resource_id", "category", "attributes"}
        ):
            raise ValueError("Expected resource requires resource_id and category")
        rid, category = item["resource_id"], item["category"]
        if not isinstance(rid, str) or not rid or not isinstance(category, str) or category not in (
            "brew_formula", "brew_cask", "app", "pkg_receipt", "launchd", "macos_build", "ollama_model"
        ):
            raise ValueError("Invalid expected resource")
        prefix = "macos" if category == "macos_build" else category
        if not rid.startswith(prefix + ":"):
            raise ValueError("Resource identifier/category mismatch")
        if rid in entries:
            if entries[rid] != item:
                raise ValueError("Conflicting expected resource: " + rid)
            continue
        attrs = item.get("attributes", {})
        if not isinstance(attrs, dict) or any(
            not isinstance(k, str) or not isinstance(v, (str, int, float, bool, type(None)))
            for k, v in attrs.items()
        ):
            raise ValueError("Expected attributes must be flat scalar metadata")
        entries[rid] = item
    categories = sorted({row["category"] for row in entries.values()} | {"brew_formula"})
    return {
        "schema_version": 1,
        "managed_categories": categories,
        "resources": [entries[rid] for rid in sorted(entries)],
    }


# Only package-manager-backed resources from role defaults are considered.
# Not all enabled features install a Homebrew package (e.g. Codex, Canon scan).
_ROLE_PACKAGES = {
    "cloud_cli": {
        "brew_formula": {"aws": "awscli", "azure": "azure-cli", "github": "gh"},
        "brew_cask": {"gcp": "gcloud-cli"},
    },
    "kubernetes_tools": {
        "brew_formula": {"oc": "openshift-cli", "kubectl": "kubernetes-cli",
                         "helm": "helm", "k9s": "k9s", "kubectx": "kubectx",
                         "stern": "stern", "kustomize": "kustomize", "skopeo": "skopeo"},
    },
    "network_tools": {
        "brew_formula": {"openvpn": "openvpn", "bind": "bind", "mtr": "mtr", "nmap": "nmap"},
        "brew_cask": {"bruno": "bruno", "wireshark": "wireshark-app"},
    },
    "development_tools": {
        "brew_formula": {"nodejs": "node", "precommit": "pre-commit"},
    },
    "database_tools": {
        "brew_cask": {"pgadmin": "pgadmin4", "podman_desktop": "podman-desktop"},
    },
    "desktop_apps": {
        "brew_cask": {
            "chrome": "google-chrome", "vscode": "visual-studio-code",
            "claude": "claude", "microsoft_365": "microsoft-office",
            "ollama": "ollama-app",
            "appcleaner": "appcleaner", "stats": "stats", "raycast": "raycast",
            "chatgpt": "chatgpt", "nextcloud": "nextcloud",
            "rectangle": "rectangle", "displaylink": "displaylink",
            "obsidian": "obsidian", "discord": "discord",
            "hidden_bar": "hiddenbar", "webex": "webex",
        },
    },
    "terminal": {"brew_cask": {"iterm2": "iterm2", "ghostty": "ghostty"}},
}


def watchdog_role_packages(repo_root, profile=None):
    """Parse package metadata without expanding unrelated Jinja or secret variables."""
    root = Path(repo_root)
    if profile is None:
        profile = yaml.safe_load(
            (root / "inventories/group_vars/profiles/personal.yml").read_text()
        )
    if not isinstance(profile, dict):
        raise ValueError("Personal profile must be a mapping")
    defaults_by_role = {}
    for role in _ROLE_PACKAGES:
        defaults = yaml.safe_load((root / "roles" / role / "defaults/main.yml").read_text())
        if not isinstance(defaults, dict):
            raise ValueError("Missing package role defaults: " + role)
        defaults_by_role[role] = defaults
    selection = {"brew_formula": set(), "brew_cask": set(), "ollama_model": set()}
    for role, categories in _ROLE_PACKAGES.items():
        defaults = defaults_by_role.get(role)
        if not isinstance(defaults, dict):
            raise ValueError("Missing package role defaults: " + role)
        prefix = role + "_"
        def setting(suffix):
            name = prefix + suffix
            return profile[name] if name in profile else defaults.get(name)
        state = setting("state")
        if state not in ("present", "absent"):
            raise ValueError("Unexpected package installation state for " + role)
        if state != "present":
            continue
        install_all = setting("install_all") if role not in ("development_tools",) else setting("install_all")
        if not isinstance(install_all, bool) and install_all is not None:
            raise ValueError("Invalid install_all setting for " + role)
        for category, packages in categories.items():
            for key, package in packages.items():
                enabled = setting(key + "_enabled")
                if not isinstance(enabled, bool):
                    raise ValueError("Invalid package enabled flag: " + prefix + key)
                # desktop apps Claude/Microsoft 365 explicitly check their enabled
                # flags without the install_all fallback.
                explicit = role == "desktop_apps" and key in {"claude", "microsoft_365", "ollama"}
                if enabled or (install_all and not explicit):
                    selection[category].add(package)
    terminal = defaults_by_role["terminal"]
    terminal_setting = lambda key: profile[key] if key in profile else terminal.get(key)
    if terminal_setting("terminal_state") == "present":
        fonts = terminal_setting("terminal_nerdfonts")
        if not isinstance(fonts, list) or any(not isinstance(x, str) or not x for x in fonts):
            raise ValueError("Invalid terminal Nerd Fonts")
        if terminal_setting("terminal_install_nerdfonts") is True:
            selection["brew_cask"].update(fonts)
        # Only the selected terminal emulator is provisioned.
        emulator = terminal_setting("terminal_emulator")
        if emulator not in ("iterm2", "ghostty"):
            raise ValueError("Invalid terminal emulator")
        unselected = {"ghostty" if emulator == "iterm2" else "iterm2"}
        selection["brew_cask"].difference_update(unselected)
    desktop_defaults = defaults_by_role["desktop_apps"]
    enabled = profile.get("desktop_apps_ollama_enabled", desktop_defaults["desktop_apps_ollama_enabled"])
    models = profile.get("desktop_apps_ollama_models", desktop_defaults["desktop_apps_ollama_models"])
    if not isinstance(models, list) or any(not isinstance(name, str) or not name for name in models):
        raise ValueError("Invalid Ollama model list")
    if enabled and "ollama-app" in selection["brew_cask"]:
        selection["ollama_model"].update(models)
    return {category: sorted(selection[category]) for category in selection}


class FilterModule:
    def filters(self):
        return {"watchdog_manifest": watchdog_manifest, "watchdog_role_packages": watchdog_role_packages}

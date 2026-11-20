"""Build the watchdog's strict JSON contract from non-secret Ansible variables."""
from __future__ import annotations


def watchdog_manifest(common, extra, resources):
    if not all(isinstance(values, list) for values in (common, extra, resources)):
        raise ValueError("Expected-state package and resource inputs must be lists")
    entries = {}
    for name in common + extra:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("Invalid Homebrew formula name")
        rid = "brew_formula:" + name
        entries[rid] = {"resource_id": rid, "category": "brew_formula"}
    for item in resources:
        if not isinstance(item, dict) or set(item) not in (
            {"resource_id", "category"}, {"resource_id", "category", "attributes"}
        ):
            raise ValueError("Expected resource requires resource_id and category")
        rid, category = item["resource_id"], item["category"]
        if not isinstance(rid, str) or not rid or not isinstance(category, str) or category not in (
            "brew_formula", "brew_cask", "app", "pkg_receipt", "launchd", "macos_build"
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


class FilterModule:
    def filters(self):
        return {"watchdog_manifest": watchdog_manifest}

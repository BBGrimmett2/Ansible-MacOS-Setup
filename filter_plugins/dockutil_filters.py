"""Small, testable transformations for dockutil's tab-separated output."""

from urllib.parse import unquote, urlparse


def dockutil_app_paths(output):
    """Read the ordered app paths from `dockutil --list`.

    dockutil lists records as label<TAB>path<TAB>section<TAB>plist. The
    persistent-apps path may be a file:// URL with percent-encoded spaces.
    Ignore persistent-others (folders/stacks) and macOS's fixed Finder tile.
    """
    paths = []
    for line in output.splitlines():
        fields = line.split("\t")
        if len(fields) < 3 or fields[2].strip() not in ("persistent-apps", "apps"):
            continue

        location = fields[1].strip()
        if location.startswith("file://"):
            location = unquote(urlparse(location).path)
        if location:
            paths.append(location.rstrip("/"))
    return paths


class FilterModule:
    """Ansible custom filters."""

    def filters(self):
        return {"dockutil_app_paths": dockutil_app_paths}

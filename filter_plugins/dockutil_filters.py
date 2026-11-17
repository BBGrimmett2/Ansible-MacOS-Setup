"""Small, testable transformations for dockutil's tab-separated output."""


def dockutil_app_paths(output):
    """Return ordered application paths from `dockutil --list`.

    dockutil lists records as: label<TAB>path<TAB>section<TAB>plist.
    Exclude Downloads/other persistent folders; Finder is managed by macOS.
    """
    paths = []
    for line in output.splitlines():
        fields = line.split("\t")
        if len(fields) >= 3 and fields[2].strip() == "apps":
            path = fields[1].strip()
            if path:
                paths.append(path)
    return paths


class FilterModule:
    """Ansible custom filters."""

    def filters(self):
        return {"dockutil_app_paths": dockutil_app_paths}

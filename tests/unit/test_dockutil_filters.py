"""Unit tests for Dock idempotency transformation."""

import unittest

from filter_plugins.dockutil_filters import dockutil_app_paths


class DockutilAppPathsTests(unittest.TestCase):
    def test_url_paths_order_and_non_apps(self):
        output = (
            "Google Chrome\tfile:///Applications/Google%20Chrome.app/\tpersistent-apps\t/Users/test/Library/Preferences/com.apple.dock.plist\n"
            "Visual Studio Code\tfile:///Applications/Visual%20Studio%20Code.app/\tpersistent-apps\t/Users/test/Library/Preferences/com.apple.dock.plist\n"
            "Downloads\tfile:///Users/test/Downloads/\tpersistent-others\t/Users/test/Library/Preferences/com.apple.dock.plist\n"
        )
        self.assertEqual(
            dockutil_app_paths(output),
            ["/Applications/Google Chrome.app", "/Applications/Visual Studio Code.app"],
        )

    def test_current_dockutil_persistent_apps_output(self):
        output = (
            "Google Chrome\\t/Applications/Google Chrome.app\\tpersistentApps\\t/Users/test/Library/Preferences/com.apple.dock.plist\\t\\n"
            "Visual Studio Code\\t/Applications/Visual Studio Code.app\\tpersistentApps\\t/Users/test/Library/Preferences/com.apple.dock.plist\\t\\n"
            "System Settings\\t/System/Applications/System Settings.app\\tpersistentApps\\t/Users/test/Library/Preferences/com.apple.dock.plist\\t\\n"
            "Downloads\\t/Users/test/Downloads\\tpersistentOthers\\t/Users/test/Library/Preferences/com.apple.dock.plist\\t\\n"
        )
        self.assertEqual(dockutil_app_paths(output), [
            "/Applications/Google Chrome.app",
            "/Applications/Visual Studio Code.app",
            "/System/Applications/System Settings.app",
        ])

    def test_plain_paths_and_empty_output(self):
        self.assertEqual(
            dockutil_app_paths("ChatGPT\t/Applications/ChatGPT.app\tapps\t/Users/test/Library/Preferences/com.apple.dock.plist"),
            ["/Applications/ChatGPT.app"],
        )
        self.assertEqual(dockutil_app_paths(""), [])


if __name__ == "__main__":
    unittest.main()

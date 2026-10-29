import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tvopt
from tvopt import (
    classify,
    decide,
    parse_pm_list,
    pm_command,
    render_rollback_script,
    restore_actions,
)


INSTALLED = [
    "com.cvte.gaia.ad.service",
    "com.cvte.wonder.cloud.service",
    "com.cvte.industries",
    "com.cvte.tv.pictorial",
    "com.cvte.tv.steward",
    "com.cvte.tv.weather",
    "com.cvte.tv.launcher.space",
    "com.cvte.tv.globalui",
    "com.cvte.tv.setting",
    "com.cvte.fac.menu",
    "com.cvte.license.at",
    "com.hisilicon.rmservice",
    "com.hisilicon.miracast",
    "com.stark.store",
    "com.google.android.feedback",
    "com.google.android.youtube.tv",
    "com.netflix.ninja",
    "ru.kinopoisk.tv",
    "ru.yandex.music",
    "com.happproxy",
    "com.android.vending",
    "com.android.systemui",
    "com.google.android.gms",
]


class ClassifyTest(unittest.TestCase):
    def test_user_apps_and_board_stay(self):
        groups = classify(INSTALLED)
        for name in (
            "ru.kinopoisk.tv",
            "ru.yandex.music",
            "com.happproxy",
            "com.google.android.youtube.tv",
            "com.netflix.ninja",
            "com.android.vending",
            "com.android.systemui",
            "com.google.android.gms",
            "com.cvte.tv.launcher.space",
            "com.cvte.tv.globalui",
            "com.cvte.tv.setting",
            "com.hisilicon.rmservice",
            "com.hisilicon.miracast",
            "com.stark.store",
            "com.cvte.tv.weather",
            "com.cvte.fac.menu",
            "com.cvte.license.at",
        ):
            self.assertIn(name, groups["keep"], name)
            self.assertNotIn(name, groups["disable"], name)

    def test_only_ads_and_cleaner_are_disabled(self):
        groups = classify(INSTALLED)
        self.assertEqual(
            groups["disable"],
            [
                "com.cvte.gaia.ad.service",
                "com.cvte.industries",
                "com.cvte.tv.pictorial",
                "com.cvte.tv.steward",
                "com.cvte.wonder.cloud.service",
                "com.google.android.feedback",
            ],
        )

    def test_factory_in_candidate_list_still_stays(self):
        self.assertEqual(decide("com.cvte.fac.menu"), "keep")
        self.assertEqual(decide("com.cvte.gaia.ad.service"), "disable")

    def test_unknown_package_is_left_alone(self):
        self.assertEqual(decide("com.example.game"), "leave")


class RollbackTest(unittest.TestCase):
    def test_restore_reenables_only_what_we_turned_off(self):
        enabled = ["com.cvte.tv.steward", "ru.kinopoisk.tv"]
        disabled = ["com.old.junk"]
        current_disabled = ["com.cvte.tv.steward", "com.old.junk"]
        self.assertEqual(
            restore_actions(enabled, disabled, current_disabled),
            [("enable", "com.cvte.tv.steward")],
        )

    def test_restore_puts_back_a_package_that_was_already_off(self):
        actions = restore_actions(
            ["ru.kinopoisk.tv"],
            ["com.old.junk"],
            [],
        )
        self.assertEqual(actions, [("disable", "com.old.junk")])

    def test_factory_is_not_disabled_by_rollback(self):
        actions = restore_actions(["com.cvte.tv.launcher.space"], ["com.cvte.fac.menu"], [])
        self.assertEqual(actions, [])

    def test_script_enables_saved_packages_and_never_uninstalls(self):
        script = render_rollback_script(
            ["ru.kinopoisk.tv", "com.cvte.tv.steward"],
            ["com.old.junk", "com.cvte.fac.menu"],
        )
        self.assertIn("pm enable --user 0 ru.kinopoisk.tv", script)
        self.assertIn("pm enable --user 0 com.cvte.tv.steward", script)
        self.assertIn("pm disable-user --user 0 com.old.junk", script)
        self.assertNotIn("com.cvte.fac.menu", script)
        self.assertNotIn("uninstall", script)

    def test_commands_reject_a_broken_name(self):
        with self.assertRaises(ValueError):
            pm_command("disable", "com.foo; rm -rf /")

    def test_parse_pm_list(self):
        self.assertEqual(
            parse_pm_list("package:ru.kinopoisk.tv\npackage:com.happproxy\nмусор\n"),
            ["com.happproxy", "ru.kinopoisk.tv"],
        )

    def test_adb_program_finds_a_nested_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "platform-tools" / "platform-tools"
            nested.mkdir(parents=True)
            exe = nested / "adb.exe"
            exe.write_bytes(b"")
            with mock.patch.object(tvopt, "ROOT", root):
                found = tvopt.adb_program()
        self.assertEqual(Path(found), exe)

    def test_missing_dll_is_reported_before_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "platform-tools"
            folder.mkdir()
            (folder / "adb.exe").write_bytes(b"")
            with mock.patch.object(tvopt, "ROOT", root):
                reason = tvopt.missing_adb_reason()
        self.assertIn("AdbWinApi.dll", reason or "")


if __name__ == "__main__":
    unittest.main()

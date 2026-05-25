import builtins
import unittest
from unittest.mock import patch

from src.dependency_checker import DependencyChecker, check_dependencies_quick


class DependencyCheckerTests(unittest.TestCase):
    def test_check_all_reports_available_tools_and_no_missing_packages(self):
        checker = DependencyChecker()

        with (
            patch("src.dependency_checker.shutil.which", return_value="tool"),
            patch.object(builtins, "__import__", return_value=object()),
        ):
            status = checker.check_all()

        self.assertTrue(status["ffmpeg"])
        self.assertTrue(status["fpcalc"])
        self.assertEqual(status["python_packages"], ([], []))

    def test_check_python_packages_splits_required_and_optional_missing(self):
        checker = DependencyChecker()
        missing = {"PIL", "mutagen", "pylast"}
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name in missing:
                raise ImportError(name)
            return real_import("types", *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=fake_import):
            required, optional = checker.check_python_packages()

        self.assertEqual(required, ["Pillow"])
        self.assertIn("mutagen", optional)
        self.assertIn("pylast", optional)

    def test_quick_check_fails_when_ffmpeg_missing(self):
        with patch("src.dependency_checker.DependencyChecker.check_all") as check_all:
            check_all.return_value = {
                "ffmpeg": False,
                "fpcalc": True,
                "python_packages": ([], []),
                "system": "Windows",
            }

            self.assertFalse(check_dependencies_quick())

    def test_format_status_includes_install_hints_for_missing_dependencies(self):
        checker = DependencyChecker()
        status = {
            "ffmpeg": False,
            "fpcalc": False,
            "python_packages": (["Pillow"], ["pylast"]),
            "system": checker.system,
        }

        message = checker.format_status_message(status)

        self.assertIn("FFmpeg: Missing", message)
        self.assertIn("Chromaprint", message)
        self.assertIn("pip install Pillow", message)
        self.assertIn("pip install pylast", message)


if __name__ == "__main__":
    unittest.main()

"""Smoke checks for the installed distribution, independent of experiments."""

import importlib
import unittest
from importlib.metadata import distribution


class PackageTests(unittest.TestCase):
    def test_installed_distribution_contains_importable_packages(self):
        installed = distribution("dark-fluid-hypothesis")
        self.assertEqual(installed.metadata["Name"], "dark-fluid-hypothesis")
        for name in ("darkfluid", "darkfluid.integrators"):
            with self.subTest(package=name):
                module = importlib.import_module(name)
                self.assertIsNotNone(module.__file__)


if __name__ == "__main__":
    unittest.main()

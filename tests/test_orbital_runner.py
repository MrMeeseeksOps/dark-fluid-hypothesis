"""Exercise the dependency-free orbital CLI and its retained artifacts."""

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "experiments/002_orbital_dynamics/run.py"


class OrbitalRunnerTests(unittest.TestCase):
    def test_artifacts_and_invalid_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [
                sys.executable,
                str(RUNNER),
                "--no-plots",
                "--output-dir",
                directory,
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = Path(result.stdout.strip())
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(summary["steps"], 400)
            self.assertEqual(summary["initial_state"], [1, 0, 0, 1])
            with (output / "trajectory.csv").open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 401)
            self.assertEqual(float(rows[-1]["t"]), summary["final_time"])
            self.assertEqual(
                summary["sha256"]["trajectory.csv"],
                hashlib.sha256((output / "trajectory.csv").read_bytes()).hexdigest(),
            )
            self.assertFalse((output / "diagnostics.png").exists())
            invalid = subprocess.run(
                command + ["--eccentricity", "1"], capture_output=True, text=True
            )
            self.assertEqual(invalid.returncode, 2)
            self.assertIn("eccentricity", invalid.stderr)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

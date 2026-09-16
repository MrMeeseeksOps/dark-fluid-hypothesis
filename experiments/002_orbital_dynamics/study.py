"""Run the predefined convergence and long-duration study, retaining provenance."""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs/002_orbital_dynamics/study")
    )
    args = parser.parse_args()
    results = []
    for eccentricity in (0.0, 0.5):
        for method, resolutions in (
            ("euler", (4000, 8000, 16000)),
            ("rk4", (400, 800, 1600)),
        ):
            previous = None
            for periods, resolution in [(1, n) for n in resolutions] + [(100, 400)]:
                command = [
                    sys.executable,
                    str(Path(__file__).with_name("run.py")),
                    "--method",
                    method,
                    "--eccentricity",
                    str(eccentricity),
                    "--periods",
                    str(periods),
                    "--steps-per-period",
                    str(resolution),
                    "--output-dir",
                    str(args.output_dir),
                    "--no-plots",
                ]
                directory = Path(subprocess.check_output(command, text=True).strip())
                summary = json.loads((directory / "summary.json").read_text())
                error = summary["metrics"]["final_combined_error"]
                summary["artifact_directory"] = str(directory)
                summary["study"] = "convergence" if periods == 1 else "long_duration"
                summary["observed_order"] = (
                    math.log2(previous / error)
                    if previous is not None and periods == 1
                    else None
                )
                results.append(summary)
                previous = error
    destination = args.output_dir / "measurements.json"
    destination.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    print(destination)


if __name__ == "__main__":
    main()

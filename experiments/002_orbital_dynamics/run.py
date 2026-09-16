"""Run the orbital dynamics experiment; see README.md for reproduction commands."""

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from darkfluid.integrators import euler_step, rk4_step
from darkfluid.mechanics import KeplerOrbit, diagnose, simulate

ROOT = Path(__file__).resolve().parents[2]


def command_output(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def plot(rows, directory):
    os.environ.setdefault("MPLCONFIGDIR", str(directory / "matplotlib-cache"))
    os.environ.setdefault("XDG_CACHE_HOME", str(directory / "cache"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = [r["t"] for r in rows]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), constrained_layout=True)
    orbit, energy, angular, error = axes.flat
    orbit.plot([r["x"] for r in rows], [r["y"] for r in rows], label="Numerical")
    orbit.plot(
        [r["x_exact"] for r in rows],
        [r["y_exact"] for r in rows],
        "--",
        label="Kepler reference",
    )
    orbit.plot(0, 0, "k+", label="Force center")
    orbit.set(xlabel="x [length unit]", ylabel="y [length unit]", aspect="equal")
    for ax, key, label in (
        (energy, "relative_energy_error", "Relative specific energy drift"),
        (
            angular,
            "relative_angular_momentum_error",
            "Relative specific angular momentum drift",
        ),
        (error, "combined_error", "Dimensionless state error"),
    ):
        ax.plot(t, [r[key] for r in rows], label=label)
        ax.set(xlabel="Time [time unit]", ylabel=label)
    for ax in axes.flat:
        ax.grid(alpha=0.3)
        ax.legend()
    fig.savefig(directory / "diagnostics.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("euler", "rk4"), default="rk4")
    parser.add_argument("--mu", type=float, default=1.0)
    parser.add_argument("--semimajor-axis", type=float, default=1.0)
    parser.add_argument("--eccentricity", type=float, default=0.0)
    parser.add_argument(
        "--no-plots", action="store_true", help="Write CSV/JSON without Matplotlib"
    )
    parser.add_argument("--periods", type=int, default=1)
    parser.add_argument("--steps-per-period", type=int, default=400)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "outputs/002_orbital_dynamics"
    )
    args = parser.parse_args(argv)
    if args.periods <= 0 or args.steps_per_period <= 0:
        parser.error("periods and steps per period must be positive integers")
    try:
        model = KeplerOrbit(args.mu, args.semimajor_axis, args.eccentricity)
        count = args.periods * args.steps_per_period
        final_time = args.periods * model.period
        samples = simulate(
            model,
            {"euler": euler_step, "rk4": rk4_step}[args.method],
            final_time,
            count,
        )
        rows, metrics = diagnose(model, samples)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    created = datetime.now(timezone.utc).isoformat()
    directory = args.output_dir.resolve() / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        + "-"
        + args.method
        + "-"
        + uuid4().hex[:10]
    )
    directory.mkdir(parents=True)
    with (directory / "trajectory.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if not args.no_plots:
        plot(rows, directory)
    status = command_output(["git", "status", "--porcelain"])
    summary = {
        "created_utc": created,
        "command": [
            sys.executable,
            str(Path(__file__).resolve()),
            *(sys.argv[1:] if argv is None else argv),
        ],
        "parameters": {k: v for k, v in vars(args).items() if k != "output_dir"},
        "units": {
            "length": "L",
            "time": "T",
            "mu": "L^3/T^2",
            "energy": "L^2/T^2 (specific)",
            "angular_momentum": "L^2/T (specific)",
        },
        "initial_state": model.initial,
        "reference": "elliptic Kepler equation, bracketed bisection",
        "dt": final_time / count,
        "final_time": final_time,
        "steps": count,
        "metrics": metrics,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "pip_freeze": command_output([sys.executable, "-m", "pip", "freeze"]),
            "git_revision": command_output(["git", "rev-parse", "HEAD"]),
            "git_dirty": bool(status) if status is not None else None,
        },
        "sha256": {
            name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in ("trajectory.csv", "diagnostics.png")
            if (directory / name).exists()
        },
    }
    (directory / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    print(directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

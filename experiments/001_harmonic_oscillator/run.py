"""Run the oscillator experiment; see README.md for reproduction commands."""

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
from darkfluid.oscillator import Oscillator, diagnose, simulate

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
    fig, axes = plt.subplots(3, 1, figsize=(9, 11), constrained_layout=True)
    axes[0].plot(t, [r["x"] for r in rows], label="Numerical")
    axes[0].plot(t, [r["x_exact"] for r in rows], "--", label="Exact")
    axes[0].set(xlabel="Time [s]", ylabel="Position [m]")
    axes[1].plot([r["x"] for r in rows], [r["v"] for r in rows], label="Numerical")
    axes[1].plot(
        [r["x_exact"] for r in rows], [r["v_exact"] for r in rows], "--", label="Exact"
    )
    axes[1].set(xlabel="Position [m]", ylabel="Velocity [m/s]")
    relative = rows[0]["relative_energy_error"] is not None
    key = "relative_energy_error" if relative else "absolute_energy_error"
    axes[2].plot(t, [r[key] for r in rows], label="Numerical − initial")
    axes[2].set(
        xlabel="Time [s]",
        ylabel="Relative energy error" if relative else "Energy error [J]",
    )
    for ax in axes:
        ax.grid(alpha=0.3)
        ax.legend()
    fig.savefig(directory / "diagnostics.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("euler", "rk4"), default="rk4")
    parser.add_argument("--mass", type=float, default=1.0)
    parser.add_argument("--spring-constant", type=float, default=1.0)
    parser.add_argument("--initial-position", type=float, default=1.0)
    parser.add_argument("--initial-velocity", type=float, default=0.0)
    parser.add_argument("--periods", type=int, default=1)
    parser.add_argument("--steps-per-period", type=int, default=100)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "outputs/001_harmonic_oscillator"
    )
    args = parser.parse_args(argv)
    if args.periods <= 0 or args.steps_per_period <= 0:
        parser.error("periods and steps per period must be positive integers")
    try:
        model = Oscillator(args.mass, args.spring_constant)
        count = args.periods * args.steps_per_period
        final_time = args.periods * model.period
        samples = simulate(
            model,
            {"euler": euler_step, "rk4": rk4_step}[args.method],
            (args.initial_position, args.initial_velocity),
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
        "units": {"mass": "kg", "length": "m", "time": "s", "spring_constant": "N/m"},
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
        },
    }
    (directory / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    print(directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

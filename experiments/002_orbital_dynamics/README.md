# Experiment 002: Orbital dynamics

Compare Euler and RK4 on circular and eccentric Newtonian orbits. Measure
trajectory error against a Kepler-equation reference, specific energy drift,
and specific angular momentum drift. See [record.md](record.md) for measured
results and limitations, and [measurements.json](measurements.json) for provenance.

From the repository root, after installing `.[dev,plots]`:

```sh
python experiments/002_orbital_dynamics/run.py
python experiments/002_orbital_dynamics/run.py --eccentricity 0.5 --periods 20 --steps-per-period 800
python experiments/002_orbital_dynamics/run.py --method euler --periods 100 --steps-per-period 400
python experiments/002_orbital_dynamics/study.py
```

Add `--no-plots` to the runner to use only the standard library. The study uses
this mode for all 16 runs. It compares one-period convergence at three resolutions
and 100-period drift for each method with eccentricities 0 and 0.5. Euler uses
4000/8000/16000 steps per period to reach its asymptotic convergence regime;
RK4 uses 400/800/1600. Long runs use 400 steps per period for both methods.
These are accuracy comparisons, not equal-cost performance benchmarks.

The runner also accepts `--mu`, `--semimajor-axis`, and `--output-dir`; use
`--help` for defaults. Each unique run directory contains `trajectory.csv`,
`summary.json`, and (unless disabled) `diagnostics.png`. The summary records
configuration, initial state, environment, Git revision/dirty state, and artifact
SHA-256 hashes. Outputs default to ignored `outputs/002_orbital_dynamics/`.
The study writes an aggregate `measurements.json` in its output directory;
copy it into this experiment only when deliberately updating the curated record.

## Model and diagnostics

State is `(x, y, vx, vy)` in the relative orbital plane. The origin is the force
center; periapsis starts on the positive x axis with counterclockwise velocity.
Use consistent length L and time T units: mu has units L³/T². Defaults set mu=a=1.
For two finite masses, mu=G(m1+m2) and invariants are per unit reduced mass.
For a test particle around a fixed mass M, mu=GM and invariants are per unit
particle mass. This is relative motion, not two independent body trajectories.

Only bound reference ellipses (0 ≤ e < 1) are supported. No softening,
relativistic corrections, perturbations, adaptive stepping, or collision-event
localization are included. An evaluated zero radius raises an error. A fixed
step can cross an unresolved close encounter; finite output alone does not
establish accuracy. High eccentricity requires finer periapsis resolution.

The reference solves E − e sin(E) = nt using 80 bracketed bisection iterations.
Its independent position and velocity are compared at every sampled time.
Relative invariant drift is (value − initial)/|initial|. Combined state error is
`sqrt((position_error/a)^2 + (velocity_error/sqrt(mu/a))^2)`.
Maxima cover sampled points only. Reference phase reduction loses precision at
extremely large times. RK4 is not symplectic and does not exactly conserve energy.

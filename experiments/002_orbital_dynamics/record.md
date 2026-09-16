# Experiment 002: Orbital dynamics

Status: implemented, run, and numerically validated for the configurations below.
Full artifacts are local; durable archival is pending.

## Research question

How do Euler and RK4 reproduce known Kepler trajectories and conserve energy
and angular momentum as timestep and integration duration change?

## Mathematical assumptions

Newtonian point masses, isolated system, planar relative coordinates, no
external forces or dissipation. Consistent arbitrary L/T units with mu=a=1
in the study. Bound reference ellipses have eccentricity 0 or 0.5. Energy and
angular momentum are specific quantities. This is numerical mechanics validation,
not a test of the dark-fluid hypothesis or General Relativity.

## Governing equations

For r=(x,y), r''=−mu r/|r|³. Specific energy is epsilon=|v|²/2−mu/|r|;
specific angular momentum is h=x vy−y vx. The analytical invariants are
−mu/(2a) and sqrt(mu a(1−e²)). Initially r=(a(1−e),0) and
v=(0,sqrt(mu/a) sqrt((1+e)/(1−e))). Period T=2 pi sqrt(a³/mu).

The independent reference uses E−e sin(E)=nt, n=sqrt(mu/a³), with
x=a(cos(E)−e), y=a sqrt(1−e²) sin(E), and E'=n/(1−e cos(E)).
Velocities are obtained by differentiating these expressions.

## Numerical method and expected behavior

Forward Euler and classical RK4, fixed timesteps, no random seeds. Kepler's
equation is solved by bracketed bisection. One-period endpoint state errors should
converge with orders 1 and 4. Exact trajectories close and conserve both
invariants. Neither numerical method guarantees long-term conservation.
Euler is expected to produce much larger drift at the same timestep.

## Falsification criteria and validation tests

The implementation fails its numerical validation if refinement does not approach
the expected orders (tolerance ±0.18 for the stated resolutions), or if the
reference fails ellipse geometry, differential-equation, or invariant checks.
For e=0.5, 20 periods with RK4 at 800 steps/period must have maximum relative
energy drift <2e-7, angular momentum drift <2e-8, and endpoint state error <2e-4.
These thresholds are regression gates for this configuration, not general error
bounds. Failed numerical conservation does not falsify Newtonian physics.

Tests also cover a circular trigonometric reference with nondefault mu and a,
force normalization, a hand Euler step, invalid parameters, zero radius, and
CLI output checksums. All 21 repository tests passed on 2026-09-16; lint,
formatting, and source/wheel builds also passed.

## Reproduction record

Local runs: 2026-09-16, base revision
`3074ae09e9073ab0999e63242af7f2b531f37aba`, with uncommitted experiment changes
on `002-orbital-dynamics`. Run from the repository root:

```sh
.venv/bin/python experiments/002_orbital_dynamics/study.py
.venv/bin/python experiments/002_orbital_dynamics/run.py --eccentricity 0.5 --periods 20 --steps-per-period 800
```

[measurements.json](measurements.json) retains the 16 study summaries, exact
commands, environment versions, configuration, Git dirty state, and CSV hashes.
Full CSV files and per-run summaries remain under ignored
`outputs/002_orbital_dynamics/study/`. The separate plotted run is under
`outputs/002_orbital_dynamics/20260916T193101-rk4-36e5f0b672/`.
These local paths are not a durable archive. The recorded base revision alone
does not contain the uncommitted implementation; retain this change together
with the summaries to reproduce it.

## Simulation results

One-period refinement (successive timestep halvings):

| Eccentricity | Method | Steps per period | Observed orders | Finest endpoint state error |
| --- | --- | --- | --- | --- |
| 0 | Euler | 4000 / 8000 / 16000 | 0.984 / 0.992 | 3.316e-2 |
| 0.5 | Euler | 4000 / 8000 / 16000 | 0.919 / 0.975 | 2.321e-1 |
| 0 | RK4 | 400 / 800 / 1600 | 4.061 / 4.030 | 4.955e-11 |
| 0.5 | RK4 | 400 / 800 / 1600 | 4.126 / 4.067 | 1.242e-8 |

100 periods, 400 steps per period for both methods:

| Eccentricity | Method | Max absolute relative energy drift | Max absolute relative angular momentum drift | Endpoint state error |
| --- | --- | --- | --- | --- |
| 0 | Euler | 7.455e-1 | 9.782e-1 | 4.321 |
| 0.5 | Euler | 9.425e-1 | 5.214e-1 | 19.12 |
| 0 | RK4 | 1.669e-8 | 8.346e-9 | 1.236e-5 |
| 0.5 | RK4 | 2.955e-6 | 4.485e-7 | 6.258e-3 |

These are deterministic sampled errors, not statistical confidence intervals.
Refinement supplies evidence of discretization order; floating-point and reference
solver errors eventually limit further convergence. Small invariant drift does
not guarantee small trajectory error, as the eccentric long run illustrates.

## Conclusion

Both methods converge at their expected orders in the tested regime. Euler's
large long-duration drift makes these coarse runs unsuitable for precise orbit
prediction. RK4 substantially improves conservation and trajectory accuracy,
but still accumulates error and is not an exact conservation method. This
validates the vector dynamics foundation within the tested configurations.
High-eccentricity, collision, unbound, and relativistic dynamics remain unvalidated.
A future symplectic-method comparison would further test long-term behavior.

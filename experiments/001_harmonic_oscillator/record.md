# Experiment 001: Harmonic oscillator

Status: implemented, run, and numerically validated for the cases below.
Full trajectories and figures are local; durable external archival is pending.

## Research question

How do method and timestep affect position, velocity, phase and energy error?

## Mathematical assumptions and governing equations

One-dimensional undamped, unforced spring: x'=v, v'=−(k/m)x.
Units are kg, m and s; k is N/m. Runs use m=k=1, x(0)=1, v(0)=0,
with the analytical sine/cosine solution and E=(m v²+k x²)/2.
This is a numerical foundation check, not a test of the dark-fluid hypothesis.

## Numerical method and expected behavior

Fixed-step forward Euler and classical RK4, N+1 samples including t=0.
One-period convergence uses 100, 200 and 400 steps. Long runs use 100 periods
at 100 and 200 steps per period. Expected global orders are 1 and 4.
Euler should grow energy by (1+dt²)^N; RK4 need not conserve energy.
Phase is unwrapped from atan2(−v/omega,x), in radians.

## Falsification criteria

Orders far from 1 or 4, incorrect reference initial conditions, or failure of
Euler's energy identity indicate a numerical implementation problem. These tests
cannot falsify or support the cosmological hypothesis.

## Reproduction record

Runs performed 2026-09-15 UTC, starting revision
`bf0511268612d43261a0d2eb8c3444bbc334ed5c`, with uncommitted implementation changes.
Python, platform, exact commands, resolved dependencies, parameters, local artifact
paths and CSV/PNG SHA-256 hashes are retained in [measurements.json](measurements.json).
No random numbers are used. Generated files are ignored under
`outputs/001_harmonic_oscillator/`; no external durable artifact location is assigned.
The small measurement summaries are retained in the source tree for review.

From the repository root, after installing `.[dev,plots]`, reproduce with:

```sh
for method in euler rk4; do
  for steps in 100 200 400; do
    python experiments/001_harmonic_oscillator/run.py --method "$method" --periods 1 --steps-per-period "$steps"
  done
  for steps in 100 200; do
    python experiments/001_harmonic_oscillator/run.py --method "$method" --periods 100 --steps-per-period "$steps"
  done
done
```

## Simulation results

Final combined error has units of metres and equals
hypot(x−x_exact, (v−v_exact)/omega). Orders compare to the preceding coarser run.

| Method | Steps/period | One-period final error [m] | Observed order |
| --- | ---: | ---: | ---: |
| euler | 100 | 0.21793845 | — |
| euler | 200 | 0.10369976 | 1.071508 |
| euler | 400 | 0.050582292 | 1.035708 |
| rk4 | 100 | 8.1602051e-07 | — |
| rk4 | 200 | 5.1002781e-08 | 3.999958 |
| rk4 | 400 | 3.1876973e-09 | 3.999989 |

After 100 periods:

| Method | Steps/period | Final relative energy error | Final phase error [rad] |
| --- | ---: | ---: | ---: |
| euler | 100 | 1.2927196e+17 | -0.82488102 |
| euler | 200 | 3.7017051e+08 | -0.20658619 |
| rk4 | 100 | -8.5414281e-06 | -8.1490211e-05 |
| rk4 | 200 | -2.6701957e-07 | -5.0984207e-06 |

These are deterministic floating-point measurements, not statistical estimates.
The timestep refinement comparison estimates truncation behavior; no claim of
roundoff-independent precision is made for the final digits.

## Validation tests

All 14 unit tests pass. Oscillator checks cover hand-computed steps, exact initial
and quarter-period states, nonzero velocity at omega=2, zero-state preservation,
endpoint and sample count, invalid inputs, convergence orders within 0.08,
Euler's 100-period energy factor within 2e-12 relative error, and accumulated
Euler phase within 1e-9 radians. The alternate-frequency RK4 final error is below
2e-8 m at 400 steps per period. CLI checks reject NaN mass and fractional counts.
A zero-state CLI run verifies null relative-energy/phase metrics and absolute
energy plotting. Ruff and source/wheel builds pass.

The one- and 100-period figures at 100 steps per period were visually inspected:
Euler spirals outward and gains energy, while RK4 overlaps the reference at the
plot scale but has measurable negative energy drift. The full 100-period position
plot is dense; quantitative phase metrics remain necessary.

## Conclusion

Measured convergence supports the expected first- and fourth-order accuracy in
this regime. Euler's long-time growth matches its numerical energy identity and
is not physical energy production. RK4 has much smaller but nonzero phase and
energy errors. These checks validate this oscillator workflow at the recorded
resolutions; they do not validate future fluid or relativistic models.
Archive full artifacts before treating these runs as retained research evidence.

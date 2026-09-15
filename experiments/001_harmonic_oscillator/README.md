# Experiment 001 — Harmonic oscillator

**Status:** build guide only. `run.py` is intentionally unimplemented.
Euler and classical RK4 are available in `darkfluid.integrators`.

## Question

How do timestep and integration method affect position, velocity, phase, and
energy error in a system with a known analytical solution?

This experiment validates numerical foundations. It does not test the dark-fluid
hypothesis directly.

## Model to implement

Use a one-dimensional, undamped spring with mass `m > 0`, spring constant `k > 0`,
and angular frequency `omega = sqrt(k/m)`. Keep units consistent: for example,
kg, seconds, metres, and N/m. There is no external driving force.

Convert `x'' + omega**2*x = 0` into a first-order system:

```text
state = (x, v)
derivative(t, state) = (v, -omega**2*x)
```

For initial position `x0` and velocity `v0` at `t = 0`, the reference solution is:

```text
x_exact(t) = x0*cos(omega*t) + (v0/omega)*sin(omega*t)
v_exact(t) = -omega*x0*sin(omega*t) + v0*cos(omega*t)
E(t) = 0.5*m*v(t)**2 + 0.5*k*x(t)**2
period = 2*pi/omega
```

Start with `m = k = 1`, `x0 = 1`, `v0 = 0`. Later test nonzero `v0` and other
frequencies to catch assumptions hidden in the default case.

## Available integrator API

```python
from darkfluid.integrators import euler_step, rk4_step

# Once you have defined derivative(t, state):
next_state = rk4_step(derivative, t, (x, v), dt)
```

Both functions take `(f, t, y, dt)` and return a new tuple representing the state
at `t + dt`. Your derivative receives a tuple and must return the same number
of finite real components. Neither method manages time, stores trajectories,
chooses a timestep, or estimates error. A scalar ODE uses a one-element sequence.

Classical RK4 uses four slope evaluations with weights `(1/6, 1/3, 1/3, 1/6)`
and stage times `(0, 1/2, 1/2, 1)`.

## Build checklist

1. **Model functions:** implement the derivative, reference solution, and energy
   calculation. Keep them independent of plotting and file output.
2. **Simulation loop:** accept a step function, initial state, final time, and
   step count `N`. Set `dt = final_time/N`, store the initial sample, then take
   exactly `N` steps using `t_n = n*dt`. Return `N+1` samples. This avoids a
   floating-point `while t < final_time` loop overshooting the endpoint.
3. **Diagnostics:** evaluate the reference solution at every sample time and
   calculate the errors below.
4. **Runner:** implement `run.py` with a `main()` and `if __name__ == "__main__"`
   guard. Use `argparse` for method (`euler` or `rk4`), mass, spring constant,
   initial position/velocity, number of periods, steps per period, and output
   directory. Reject nonfinite parameters, nonpositive mass/spring constant,
   and nonpositive step/period counts. Require integer counts for this first runner.
5. **Output:** write a CSV trajectory and a JSON summary containing parameters,
   method, actual `dt`, error metrics, and environment/revision information.
   Give each run its own directory so comparisons do not overwrite each other.
6. **Figures:** plot position versus time with the reference solution, the
   `(x, v)` phase portrait, and relative energy error versus time. Add a plotting
   dependency only when implementing this step.
7. **Record:** fill in the research record template and update the experiment
   log with measured results and the commands used.

Suggested CSV columns:

```text
t,x,v,x_exact,v_exact,energy,position_error,velocity_error,relative_energy_error
```

Use `outputs/001_harmonic_oscillator/<run-id>/` for generated files. Record durable
artifact locations before treating a run as retained evidence; see the
[development guide](../../docs/development.md).

## Diagnostics and validation targets

- **Position/velocity error:** report maximum absolute errors over the trajectory.
- **Combined error:** use `sqrt((x-x_exact)**2 + ((v-v_exact)/omega)**2)` so both
  components have the same units. Report the final value for convergence studies.
- **Energy drift:** report `(E(t)-E(0))/E(0)` and its maximum absolute value.
  For the all-zero initial state, relative energy error is undefined; report
  absolute energy error instead and verify that the state stays zero.
- **Phase error:** for a nonzero trajectory, unwrap
  `atan2(-v/omega, x)` across samples, then subtract the exact unwrapped phase.
  Use sufficiently fine sampling to resolve phase changes; phase is undefined
  for the zero state.

### Short-time accuracy and convergence

At a fixed final time of one period, run each method with 100, 200, and 400 steps.
Halving `dt` should asymptotically reduce global error by about 2 for Euler and
16 for RK4. Calculate `p = log2(error_coarse/error_fine)`; investigate values far
from 1 and 4, respectively. Keep final time and initial conditions identical.
Avoid drawing order estimates from errors near floating-point roundoff.

### Long-time behavior

Compare 100 periods at 100 and 200 steps per period. Forward Euler's oscillator
energy grows by a factor `1 + (omega*dt)**2` per step in exact arithmetic; energy
growth is expected even though the exact physical system conserves energy.
Use this identity as an implementation check. RK4 is not energy-preserving either;
measure its drift and phase error rather than assuming conservation.

### Sanity checks

- The first sample equals the initial condition; the last is at the intended time.
- Both methods use identical sample times and initial states.
- Smaller timesteps improve short-time error in the convergence regime.
- Check nonzero initial velocity, the zero state, and at least one other frequency.
- Compare one step by hand to catch state ordering and sign mistakes.

## Completion criteria

The experiment is ready to review when the runner is reproducible, reference
comparisons and convergence measurements are recorded, and figures agree with
the quantitative diagnostics. Explain any failed checks before using the solver
for later experiments. A plausible-looking orbit alone is insufficient.

Results and conclusions are **pending**. Use the
[experiment record template](../../docs/templates/experiment-record.md) to record
them after implementation and validation.

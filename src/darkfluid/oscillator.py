"""Undamped harmonic oscillator in consistent mass, length and time units."""

from dataclasses import dataclass
from math import atan2, cos, hypot, isfinite, pi, remainder, sin, sqrt


@dataclass(frozen=True)
class Oscillator:
    """State is (position, velocity); mass and spring constant are positive."""

    mass: float = 1.0
    spring_constant: float = 1.0

    def __post_init__(self):
        for value in (self.mass, self.spring_constant):
            if not isfinite(value) or value <= 0:
                raise ValueError("mass and spring constant must be finite and positive")
        if not isfinite(self.omega) or self.omega == 0:
            raise ValueError("frequency must be finite and positive")

    @property
    def omega(self):
        return sqrt(self.spring_constant) / sqrt(self.mass)

    @property
    def period(self):
        return 2 * pi / self.omega

    def derivative(self, t, state):
        x, v = state
        return v, -self.omega * (self.omega * x)

    def exact(self, t, initial):
        x, v = initial
        angle = self.omega * t
        return x * cos(angle) + v / self.omega * sin(angle), (
            -self.omega * x * sin(angle) + v * cos(angle)
        )

    def energy(self, state):
        x, v = state
        return 0.5 * self.mass * v**2 + 0.5 * self.spring_constant * x**2


def simulate(model, step, initial, final_time, count):
    """Return N+1 (time, state) samples, taking exactly N fixed steps."""
    initial = tuple(float(value) for value in initial)
    if len(initial) != 2 or not all(isfinite(value) for value in initial):
        raise ValueError("initial state must contain two finite values")
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("step count must be a positive integer")
    if not isfinite(final_time) or final_time <= 0:
        raise ValueError("final time must be finite and positive")
    dt = final_time / count
    if dt == 0:
        raise ValueError("timestep underflow")
    samples = [(0.0, initial)]
    state = initial
    for n in range(count):
        state = step(model.derivative, n * dt, state, dt)
        samples.append((final_time if n + 1 == count else (n + 1) * dt, state))
    return samples


def diagnose(model, samples):
    """Reference errors and sampled unwrapped phase (radians).

    Phase requires omega*dt < pi and nonzero states; otherwise it is omitted.
    Relative energy error is undefined at zero initial energy.
    """
    initial = samples[0][1]
    e0 = model.energy(initial)
    nonzero = initial != (0.0, 0.0)
    phase_resolved = (
        nonzero
        and all(model.omega * (b[0] - a[0]) < pi for a, b in zip(samples, samples[1:]))
        and all(state != (0.0, 0.0) for _, state in samples)
    )
    previous = phase = phase0 = atan2(-initial[1] / model.omega, initial[0])
    rows = []
    for t, state in samples:
        x, v = state
        xe, ve = model.exact(t, initial)
        energy = model.energy(state)
        absolute = energy - e0
        phase_error = None
        if phase_resolved:
            angle = atan2(-v / model.omega, x)
            phase += remainder(angle - previous, 2 * pi)
            previous = angle
            phase_error = phase - (phase0 + model.omega * t)
        row = dict(
            t=t,
            x=x,
            v=v,
            x_exact=xe,
            v_exact=ve,
            energy=energy,
            position_error=x - xe,
            velocity_error=v - ve,
            absolute_energy_error=absolute,
            relative_energy_error=absolute / e0 if e0 else None,
            combined_error=hypot(x - xe, (v - ve) / model.omega),
            phase_error=phase_error,
        )
        if any(value is not None and not isfinite(value) for value in row.values()):
            raise ValueError("diagnostic overflow; reduce duration or timestep")
        rows.append(row)
    metrics = {
        "max_absolute_position_error": max(abs(r["position_error"]) for r in rows),
        "max_absolute_velocity_error": max(abs(r["velocity_error"]) for r in rows),
        "final_combined_error": rows[-1]["combined_error"],
        "max_absolute_energy_error": max(abs(r["absolute_energy_error"]) for r in rows),
        "max_absolute_relative_energy_error": (
            max(abs(r["relative_energy_error"]) for r in rows) if e0 else None
        ),
        "final_relative_energy_error": rows[-1]["relative_energy_error"],
        "max_absolute_phase_error": (
            max(abs(r["phase_error"]) for r in rows) if phase_resolved else None
        ),
        "final_phase_error": rows[-1]["phase_error"],
        "phase_resolved": phase_resolved,
    }
    return rows, metrics

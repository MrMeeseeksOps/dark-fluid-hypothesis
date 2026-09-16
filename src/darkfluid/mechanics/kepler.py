"""Planar Newtonian relative motion in consistent length and time units."""

from dataclasses import dataclass
from math import cos, hypot, isfinite, pi, remainder, sin, sqrt


def _state(values):
    state = tuple(float(v) for v in values)
    if len(state) != 4 or not all(isfinite(v) for v in state):
        raise ValueError("state must contain four finite values (x, y, vx, vy)")
    if hypot(*state[:2]) == 0:
        raise ValueError("point-mass collision: radius must be nonzero")
    return state


@dataclass(frozen=True)
class KeplerOrbit:
    """Elliptical reference orbit starting at periapsis, moving counterclockwise.

    mu = G*(m1+m2) for relative two-body motion (or GM for a test particle).
    Energy and angular momentum are specific quantities, per reduced mass.
    The force is unsoftened; collisions are outside this model's domain.
    """

    mu: float = 1.0
    semimajor_axis: float = 1.0
    eccentricity: float = 0.0

    def __post_init__(self):
        if any(not isfinite(v) or v <= 0 for v in (self.mu, self.semimajor_axis)):
            raise ValueError("mu and semimajor axis must be finite and positive")
        if not isfinite(self.eccentricity) or not 0 <= self.eccentricity < 1:
            raise ValueError("eccentricity must satisfy 0 <= e < 1")
        try:
            if not isfinite(self.period) or self.period <= 0:
                raise ValueError("orbital period must be finite and positive")
            _state(self.initial)
        except (OverflowError, ZeroDivisionError) as exc:
            raise ValueError("orbital parameters exceed numerical range") from exc

    @property
    def mean_motion(self):
        return sqrt(self.mu / self.semimajor_axis) / self.semimajor_axis

    @property
    def period(self):
        return 2 * pi / self.mean_motion

    @property
    def initial(self):
        a, e = self.semimajor_axis, self.eccentricity
        return (a * (1 - e), 0.0, 0.0, sqrt(self.mu / a) * sqrt((1 + e) / (1 - e)))

    def derivative(self, t, state):
        x, y, vx, vy = _state(state)
        r = hypot(x, y)
        acceleration = (self.mu / r) / r
        return vx, vy, -acceleration * (x / r), -acceleration * (y / r)

    def energy(self, state):
        x, y, vx, vy = _state(state)
        return (vx * vx + vy * vy) / 2 - self.mu / hypot(x, y)

    def angular_momentum(self, state):
        x, y, vx, vy = _state(state)
        return x * vy - y * vx

    def exact(self, t):
        """Solve E - e sin(E) = n*t by bracketed bisection (80 iterations).

        Independent of the numerical ODE integration. Time is relative to
        periapsis; phase reduction loses precision at extremely large times.
        """
        if not isfinite(t) or not isfinite(self.mean_motion * t):
            raise ValueError("reference time must be finite and in numerical range")
        mean = remainder(self.mean_motion * t, 2 * pi)
        lo, hi = -pi, pi
        for _ in range(80):
            anomaly = (lo + hi) / 2
            if anomaly - self.eccentricity * sin(anomaly) < mean:
                lo = anomaly
            else:
                hi = anomaly
        anomaly = (lo + hi) / 2
        a, e = self.semimajor_axis, self.eccentricity
        c, s = cos(anomaly), sin(anomaly)
        rate = self.mean_motion / (1 - e * c)
        b = a * sqrt((1 - e) * (1 + e))
        return a * (c - e), b * s, -a * s * rate, b * c * rate


def simulate(model, step, final_time, count):
    """Return N+1 fixed-step samples starting at the model's periapsis."""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("step count must be a positive integer")
    if not isfinite(final_time) or final_time <= 0:
        raise ValueError("final time must be finite and positive")
    dt = final_time / count
    if dt == 0:
        raise ValueError("timestep underflow")
    state = model.initial
    samples = [(0.0, state)]
    for n in range(count):
        state = _state(step(model.derivative, n * dt, state, dt))
        samples.append((final_time if n + 1 == count else (n + 1) * dt, state))
    return samples


def diagnose(model, samples):
    """Reference errors and signed invariant drift for periapsis-start samples.

    Relative drift uses the absolute initial invariant as denominator. Combined
    state error scales position by a and velocity by sqrt(mu/a), so it is unitless.
    Maxima are sampled maxima, not bounds between timesteps.
    """
    e0 = model.energy(model.initial)
    l0 = model.angular_momentum(model.initial)
    rows = []
    for t, state in samples:
        x, y, vx, vy = _state(state)
        xe, ye, vxe, vye = model.exact(t)
        energy = model.energy(state)
        angular = model.angular_momentum(state)
        position_error = hypot(x - xe, y - ye)
        velocity_error = hypot(vx - vxe, vy - vye)
        row = dict(
            t=t,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            x_exact=xe,
            y_exact=ye,
            vx_exact=vxe,
            vy_exact=vye,
            radius=hypot(x, y),
            energy=energy,
            angular_momentum=angular,
            relative_energy_error=(energy - e0) / abs(e0),
            relative_angular_momentum_error=(angular - l0) / abs(l0),
            position_error=position_error,
            velocity_error=velocity_error,
            combined_error=hypot(
                position_error / model.semimajor_axis,
                velocity_error / sqrt(model.mu / model.semimajor_axis),
            ),
        )
        if not all(isfinite(v) for v in row.values()):
            raise ValueError("diagnostic overflow; reduce duration or timestep")
        rows.append(row)
    if not rows:
        raise ValueError("at least one sample is required")
    metrics = {"final_combined_error": rows[-1]["combined_error"]}
    for key in (
        "relative_energy_error",
        "relative_angular_momentum_error",
        "position_error",
        "velocity_error",
    ):
        metrics["max_absolute_" + key] = max(abs(r[key]) for r in rows)
        metrics["final_" + key] = rows[-1][key]
    return rows, metrics

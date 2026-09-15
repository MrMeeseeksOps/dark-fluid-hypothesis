"""Classical fourth-order Runge–Kutta integration for y' = f(t, y)."""

from collections.abc import Sequence

from ._common import Derivative, State, slope, state_vector, validate_time


def rk4_step(f: Derivative, t: float, y: Sequence[float], dt: float) -> State:
    """Advance one fixed step using four slope evaluations.

    k1 = f(t, y)
    k2 = f(t + dt/2, y + dt*k1/2)
    k3 = f(t + dt/2, y + dt*k2/2)
    k4 = f(t + dt, y + dt*k3)
    y_next = y + dt*(k1 + 2*k2 + 2*k3 + k4)/6

    Uses the same finite real state-vector contract as ``euler_step``: returns
    a tuple without modifying the input; negative dt is supported and zero dt
    returns a copy without evaluating f. Invalid sizes or nonfinite values
    raise ValueError. Global accuracy is fourth order for sufficiently smooth
    problems. No adaptive error estimate or stability control is provided.
    """
    validate_time(t, dt)
    state = state_vector(y)
    if dt == 0:
        return state
    k1 = slope(f, t, state)
    midpoint1 = state_vector(tuple(value + dt * k / 2 for value, k in zip(state, k1)))
    k2 = slope(f, t + dt / 2, midpoint1)
    midpoint2 = state_vector(tuple(value + dt * k / 2 for value, k in zip(state, k2)))
    k3 = slope(f, t + dt / 2, midpoint2)
    endpoint = state_vector(tuple(value + dt * k for value, k in zip(state, k3)))
    k4 = slope(f, t + dt, endpoint)
    return state_vector(
        tuple(
            value + dt * (a + 2 * b + 2 * c + d) / 6
            for value, a, b, c, d in zip(state, k1, k2, k3, k4)
        )
    )

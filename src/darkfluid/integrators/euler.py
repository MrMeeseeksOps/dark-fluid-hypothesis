"""Forward Euler integration for first-order systems y' = f(t, y)."""

from collections.abc import Sequence

from ._common import Derivative, State, slope, state_vector, validate_time


def euler_step(f: Derivative, t: float, y: Sequence[float], dt: float) -> State:
    """Advance by one explicit Euler step: y_next = y + dt * f(t, y).

    ``y`` is a nonempty sequence of finite real numbers, including for a scalar
    ODE (use ``(value,)``). ``f`` receives an immutable state tuple and must
    return a finite sequence of equal length. The input is never modified.
    The result is a tuple. Negative timesteps integrate backwards; zero returns
    a copy without evaluating ``f``. Invalid sizes or nonfinite values raise
    ValueError. This fixed-step method has first-order global accuracy for
    sufficiently smooth problems; it provides no error or stability control.
    """
    validate_time(t, dt)
    state = state_vector(y)
    if dt == 0:
        return state
    k1 = slope(f, t, state)
    return state_vector(tuple(value + dt * k for value, k in zip(state, k1)))

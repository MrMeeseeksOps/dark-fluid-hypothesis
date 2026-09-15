"""Shared state-vector contract for explicit integration steps."""

from collections.abc import Callable, Sequence
from math import isfinite

State = tuple[float, ...]
Derivative = Callable[[float, State], Sequence[float]]


def state_vector(values: Sequence[float]) -> State:
    """Copy a nonempty, finite, real state into an immutable tuple."""
    state = tuple(float(value) for value in values)
    if not state or not all(isfinite(value) for value in state):
        raise ValueError("state must contain at least one value and all must be finite")
    return state


def validate_time(t: float, dt: float) -> None:
    if not all(isfinite(value) for value in (t, dt, t + dt)):
        raise ValueError("t, dt, and t + dt must be finite")


def slope(f: Derivative, t: float, y: State) -> State:
    result = state_vector(f(t, y))
    if len(result) != len(y):
        raise ValueError("derivative must have the same number of components as state")
    return result

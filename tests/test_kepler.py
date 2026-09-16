"""Independent force, Kepler geometry, convergence and invariant checks."""

import math
import unittest

from darkfluid.integrators import euler_step, rk4_step
from darkfluid.mechanics import KeplerOrbit, diagnose, simulate


class KeplerTests(unittest.TestCase):
    def test_force_and_hand_step(self):
        model = KeplerOrbit(mu=10)
        for actual, expected in zip(
            model.derivative(0, (3, 4, 1, 2)), (1, 2, -0.24, -0.32)
        ):
            self.assertAlmostEqual(actual, expected)
        model = KeplerOrbit()
        self.assertEqual(
            simulate(model, euler_step, 0.1, 1)[-1], (0.1, (1, 0.1, -0.1, 1))
        )

    def test_circular_reference(self):
        model = KeplerOrbit(mu=8, semimajor_axis=2)
        for t in (0, 0.3, model.period / 4, -0.5):
            expected = (
                2 * math.cos(t),
                2 * math.sin(t),
                -2 * math.sin(t),
                2 * math.cos(t),
            )
            for actual, value in zip(model.exact(t), expected):
                self.assertAlmostEqual(actual, value, delta=2e-14)

    def test_ellipse_geometry_and_invariants(self):
        for e in (0, 0.5, 0.95):
            model = KeplerOrbit(2, 3, e)
            for fraction in (0, 0.1, 0.25, 0.5, 0.9, 1):
                state = model.exact(fraction * model.period)
                x, y, _, _ = state
                self.assertAlmostEqual(
                    ((x + 3 * e) / 3) ** 2 + y * y / (9 * (1 - e * e)), 1, delta=1e-13
                )
                self.assertAlmostEqual(model.energy(state), -2 / 6, delta=1e-12)
                self.assertAlmostEqual(
                    model.angular_momentum(state),
                    math.sqrt(6 * (1 - e * e)),
                    delta=1e-13,
                )
            self.assertAlmostEqual(model.exact(model.period / 2)[0], -3 * (1 + e))
            # Check time parameterization against the differential equation.
            t, dt = 0.23 * model.period, 1e-5
            before, after = model.exact(t - dt), model.exact(t + dt)
            for a, b, slope in zip(before, after, model.derivative(t, model.exact(t))):
                self.assertAlmostEqual((b - a) / (2 * dt), slope, delta=1e-8)

    def test_convergence(self):
        for e in (0, 0.5):
            model = KeplerOrbit(eccentricity=e)
            for step, expected_order, counts in (
                (euler_step, 1, (4000, 8000, 16000)),
                (rk4_step, 4, (400, 800, 1600)),
            ):
                errors = []
                for count in counts:
                    state = simulate(model, step, model.period, count)[-1]
                    _, metrics = diagnose(model, [state])
                    errors.append(metrics["final_combined_error"])
                for a, b in zip(errors, errors[1:]):
                    self.assertAlmostEqual(math.log2(a / b), expected_order, delta=0.18)

    def test_long_run_invariants_and_drift(self):
        model = KeplerOrbit(eccentricity=0.5)
        _, metrics = diagnose(
            model, simulate(model, rk4_step, 20 * model.period, 16000)
        )
        self.assertLess(metrics["max_absolute_relative_energy_error"], 2e-7)
        self.assertLess(metrics["max_absolute_relative_angular_momentum_error"], 2e-8)
        self.assertLess(metrics["final_combined_error"], 2e-4)
        _, euler = diagnose(model, simulate(model, euler_step, model.period, 400))
        self.assertGreater(euler["final_relative_energy_error"], 0.1)
        self.assertGreater(euler["final_relative_angular_momentum_error"], 0.01)

    def test_invalid_parameters_and_collision(self):
        for value in (0, -1, math.inf, math.nan):
            for key in ("mu", "semimajor_axis"):
                with self.assertRaises(ValueError):
                    KeplerOrbit(**{key: value})
        for e in (-0.1, 1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                KeplerOrbit(eccentricity=e)
        model = KeplerOrbit()
        for state in ((0, 0, 1, 1), (1, 2), (1, 0, math.nan, 0)):
            with self.assertRaises(ValueError):
                model.derivative(0, state)
        for count in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                simulate(model, rk4_step, 1, count)
        for t in (0, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                simulate(model, rk4_step, t, 10)
        with self.assertRaises(ValueError):
            diagnose(model, [])

"""Analytical and contract checks, independent of experiment runners."""

import math
import unittest

from darkfluid.integrators import euler_step, rk4_step

METHODS = (euler_step, rk4_step)


class IntegratorTests(unittest.TestCase):
    def test_constant_vector_derivative_and_input_preservation(self):
        for method in METHODS:
            for dt in (0.25, -0.25):
                with self.subTest(method=method.__name__, dt=dt):
                    original = [1.0, 3.0]
                    result = method(lambda t, y: (2.0, -4.0), 1.0, original, dt)
                    self.assertEqual(result, (1 + 2 * dt, 3 - 4 * dt))
                    self.assertEqual(original, [1.0, 3.0])

    def test_zero_step_does_not_call_derivative(self):
        def unexpected(t, y):
            self.fail("zero step evaluated derivative")

        for method in METHODS:
            self.assertEqual(method(unexpected, 0, [2], 0), (2.0,))

    def test_time_dependent_rhs(self):
        # y' = t*y, y(1) = 2: check nonautonomous stage times and states.
        seen = []

        def rhs(t, y):
            seen.append((t, y))
            return (t * y[0],)

        self.assertAlmostEqual(euler_step(rhs, 1, (2,), 0.2)[0], 2.4)
        seen.clear()
        self.assertAlmostEqual(rk4_step(rhs, 1, (2,), 0.2)[0], 2.4921429333333333)
        self.assertEqual(len(seen), 4)
        for (t, y), (expected_t, expected_y) in zip(
            seen, ((1, 2), (1.1, 2.2), (1.1, 2.242), (1.2, 2.49324))
        ):
            self.assertAlmostEqual(t, expected_t)
            self.assertAlmostEqual(y[0], expected_y)

    def test_global_convergence_against_exponential(self):
        for method, order in ((euler_step, 1), (rk4_step, 4)):
            errors = []
            for count in (20, 40, 80):
                y = (1.0,)
                for n in range(count):
                    y = method(lambda t, state: state, n / count, y, 1 / count)
                errors.append(abs(y[0] - math.e))
            for coarse, fine in zip(errors, errors[1:]):
                with self.subTest(method=method.__name__):
                    self.assertAlmostEqual(math.log2(coarse / fine), order, delta=0.08)

    def test_coupled_rotation(self):
        # Exact state at t=1 is (cos(1), -sin(1)).
        for method, tolerance in ((euler_step, 0.006), (rk4_step, 1e-9)):
            y = (1.0, 0.0)
            for n in range(100):
                y = method(lambda t, s: (s[1], -s[0]), n / 100, y, 0.01)
            self.assertLess(
                math.hypot(y[0] - math.cos(1), y[1] + math.sin(1)), tolerance
            )

    def test_invalid_states_times_and_derivatives(self):
        for method in METHODS:
            for state in ((), (math.nan,), (math.inf,)):
                with self.subTest(method=method.__name__, state=state):
                    with self.assertRaises(ValueError):
                        method(lambda t, y: y, 0, state, 0.1)
            for t, dt in ((math.inf, 0.1), (0, math.nan), (1e308, 1e308)):
                with self.assertRaises(ValueError):
                    method(lambda t, y: y, t, (1,), dt)
            for derivative in ((), (1, 2), (math.nan,), (math.inf,)):
                with self.assertRaises(ValueError):
                    method(lambda t, y: derivative, 0, (1,), 0.1)

    def test_rejects_nonfinite_intermediate_or_final_state(self):
        for method in METHODS:
            with self.assertRaises(ValueError):
                method(lambda t, y: (1e308,), 0, (1e308,), 4)


if __name__ == "__main__":
    unittest.main()

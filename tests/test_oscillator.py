"""Analytical oscillator validation, including convergence and phase winding."""

import math
import unittest

from darkfluid.integrators import euler_step, rk4_step
from darkfluid.oscillator import Oscillator, diagnose, simulate


class OscillatorTests(unittest.TestCase):
    def test_reference_and_nondefault_frequency(self):
        model = Oscillator(2, 8)
        self.assertEqual(model.derivative(0, (3, 4)), (4, -12))
        self.assertEqual(model.exact(0, (3, 4)), (3, 4))
        x, v = model.exact(model.period / 4, (3, 4))
        self.assertAlmostEqual(x, 2)
        self.assertAlmostEqual(v, -6)
        self.assertAlmostEqual(model.energy((x, v)), model.energy((3, 4)))
        rows, metrics = diagnose(
            model, simulate(model, rk4_step, (3, 4), model.period, 400)
        )
        self.assertLess(metrics["final_combined_error"], 2e-8)
        self.assertEqual(rows[0]["velocity_error"], 0)

    def test_times_and_hand_step(self):
        model = Oscillator()
        for step in (euler_step, rk4_step):
            samples = simulate(model, step, (1, 0), 0.1, 1)
            self.assertEqual(samples[0], (0, (1, 0)))
            self.assertEqual(len(samples), 2)
            self.assertEqual(samples[-1][0], 0.1)
        self.assertEqual(simulate(model, euler_step, (1, 0), 0.1, 1)[-1][1], (1, -0.1))
        x, v = simulate(model, rk4_step, (1, 0), 0.1, 1)[-1][1]
        self.assertAlmostEqual(x, 1 - 0.1**2 / 2 + 0.1**4 / 24)
        self.assertAlmostEqual(v, -0.1 + 0.1**3 / 6)

    def test_convergence(self):
        model = Oscillator()
        for step, order in ((euler_step, 1), (rk4_step, 4)):
            errors = []
            for count in (100, 200, 400):
                _, metrics = diagnose(
                    model, simulate(model, step, (1, 0), model.period, count)
                )
                errors.append(metrics["final_combined_error"])
            for a, b in zip(errors, errors[1:]):
                self.assertAlmostEqual(math.log2(a / b), order, delta=0.08)

    def test_energy_identity_and_unwrapped_phase(self):
        model = Oscillator()
        count = 10000
        dt = model.period * 100 / count
        rows, metrics = diagnose(
            model, simulate(model, euler_step, (1, 0), model.period * 100, count)
        )
        predicted = (1 + dt**2) ** count
        self.assertAlmostEqual(rows[-1]["energy"] / (0.5 * predicted), 1, delta=2e-12)
        self.assertAlmostEqual(
            metrics["final_phase_error"], count * (math.atan(dt) - dt), delta=1e-9
        )

    def test_zero_and_unresolved_phase(self):
        model = Oscillator()
        for step in (euler_step, rk4_step):
            rows, metrics = diagnose(
                model, simulate(model, step, (0, 0), model.period, 100)
            )
            self.assertTrue(all(r["x"] == r["v"] == 0 for r in rows))
            self.assertIsNone(metrics["max_absolute_relative_energy_error"])
            self.assertIsNone(metrics["final_phase_error"])
            self.assertEqual(metrics["max_absolute_energy_error"], 0)
        _, metrics = diagnose(model, simulate(model, rk4_step, (1, 0), model.period, 2))
        self.assertFalse(metrics["phase_resolved"])

    def test_invalid_inputs(self):
        for value in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                Oscillator(value, 1)
            with self.assertRaises(ValueError):
                Oscillator(1, value)
        for count in (0, -1, 2.5, True):
            with self.assertRaises(ValueError):
                simulate(Oscillator(), rk4_step, (1, 0), 1, count)
        for initial in ((math.nan, 0), (1,), (1, 2, 3)):
            with self.assertRaises(ValueError):
                simulate(Oscillator(), rk4_step, initial, 1, 100)

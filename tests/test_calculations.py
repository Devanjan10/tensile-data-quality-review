import unittest

import numpy as np

from scripts.calculations import engineering_stress_mpa


class StressCalculationTests(unittest.TestCase):
    def test_known_answers_and_input_preservation(self):
        # Hand-checkable synthetic values, not experimental measurements.
        forces = np.array([0.0, 1000.0, -2.0])
        original = forces.copy()

        stress = engineering_stress_mpa(forces, area_mm2=20.0)

        np.testing.assert_allclose(
            stress,
            [0.0, 50.0, -0.1],
            rtol=0.0,
            atol=1e-12,
        )
        np.testing.assert_array_equal(forces, original)

    def test_invalid_area_is_rejected(self):
        for area in [0.0, -20.0, float("nan"), float("inf")]:
            with self.subTest(area=area):
                with self.assertRaisesRegex(ValueError, "Original area"):
                    engineering_stress_mpa([1000.0], area)

    def test_nonfinite_force_is_rejected(self):
        for force in [float("nan"), float("inf"), -float("inf")]:
            with self.subTest(force=force):
                with self.assertRaisesRegex(ValueError, "Force values"):
                    engineering_stress_mpa([force], 20.0)

    def test_stress_overflow_is_rejected(self):
        with np.errstate(over="ignore"):
            with self.assertRaisesRegex(ValueError, "Calculated stress"):
                engineering_stress_mpa([np.finfo(float).max], 0.5)

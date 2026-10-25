import unittest

import pandas as pd

from scripts.validation import validate_measurements


class ValidationTests(unittest.TestCase):
    def setUp(self):
        # Synthetic test fixture, not experimental measurements.
        self.sample = pd.DataFrame({
            "Index": [0, 1],
            "Load (N)": [-2.0, 500.0],
            "Crosshead (mm)": [0.0, 0.03],
            "Extensometer (mm)": [-0.0001, 0.025],
            "Time (sec)": [0.0, 0.02],
        })

    def test_finite_negative_readings_are_preserved(self):
        original = self.sample.copy(deep=True)
        checked = validate_measurements(self.sample)

        self.assertEqual(checked.loc[0, "Load (N)"], -2.0)
        self.assertEqual(checked.loc[0, "Extensometer (mm)"], -0.0001)
        pd.testing.assert_frame_equal(self.sample, original)

    def test_repeated_time_is_rejected(self):
        changed = self.sample.copy(deep=True)
        changed.loc[1, "Time (sec)"] = 0.0

        with self.assertRaisesRegex(ValueError, "Time must increase"):
            validate_measurements(changed)

    def test_missing_and_infinite_values_are_rejected(self):
        for value in [float("nan"), float("inf"), -float("inf")]:
            with self.subTest(value=value):
                changed = self.sample.copy(deep=True)
                changed.loc[1, "Load (N)"] = value

                with self.assertRaisesRegex(ValueError, "Missing or infinite"):
                    validate_measurements(changed)

    def test_text_in_load_is_rejected(self):
        changed = self.sample.astype(object)
        changed.loc[1, "Load (N)"] = "sensor_error"

        with self.assertRaises(ValueError):
            validate_measurements(changed)

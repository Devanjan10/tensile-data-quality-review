"""Quality-check regressions and end-to-end verification with real input."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from scripts.review import (
    DEFAULT_WORKBOOK, STRESS_COLUMN, plot_review, review_tables,
    run_review, validate_geometry, validate_stress,
)


FIXTURES = Path(__file__).parent / "fixtures"


def synthetic_tables(filename="valid_measurements.csv"):
    metadata = pd.DataFrame([json.loads((FIXTURES / "metadata.json").read_text())])
    return metadata, pd.read_csv(FIXTURES / filename)


def write_workbook(path, metadata, measurements):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        metadata.to_excel(writer, sheet_name="Sheet1", index=False)
        measurements.to_excel(writer, sheet_name="Sheet2", startrow=1, index=False)


class ReviewTests(unittest.TestCase):
    def test_synthetic_known_answer_and_input_preservation(self):
        metadata, measurements = synthetic_tables()
        original = measurements.copy(deep=True)
        report, derived = review_tables(metadata, measurements)
        self.assertEqual(report["status"], "pass_with_warnings")
        self.assertEqual(report["peak"]["calculated_stress_mpa"], 25.0)
        self.assertEqual(report["peak"]["source_index"], 1)
        self.assertEqual(report["negative_readings"]["Load (N)"], 1)
        np.testing.assert_array_equal(derived[STRESS_COLUMN], [-0.1, 25.0])
        pd.testing.assert_frame_equal(measurements, original)

    def test_labeled_corrupted_measurement_fixtures(self):
        for filename, check_name, message in (
            ("missing_load.csv", "measurements", "Missing or infinite"),
            ("duplicate_time.csv", "measurements", "Time must increase"),
            ("altered_stress.csv", "stress_calculation", "Engineering stress disagrees"),
        ):
            with self.subTest(fixture=filename):
                report, derived = review_tables(*synthetic_tables(filename))
                self.assertEqual(report["status"], "fail")
                self.assertIsNone(derived)
                finding = next(item for item in report["checks"] if item["name"] == check_name)
                self.assertEqual(finding["status"], "fail")
                self.assertIn(message, finding["message"])

    def test_invalid_dimensions_are_rejected(self):
        metadata, _ = synthetic_tables()
        for field in ("Width (mm)", "Thickness (mm)", "Area (mm²)"):
            for value in (0.0, -1.0, np.nan, np.inf, "bad"):
                with self.subTest(field=field, value=value):
                    invalid_dimensions = metadata.astype(object).copy(deep=True)
                    invalid_dimensions.loc[0, field] = value
                    with self.assertRaisesRegex(ValueError, "finite and positive"):
                        validate_geometry(invalid_dimensions)

    def test_geometry_shape_and_missing_fields(self):
        metadata, _ = synthetic_tables()
        for changed in (metadata.iloc[:0], pd.concat([metadata, metadata])):
            with self.assertRaisesRegex(ValueError, "one specimen"):
                validate_geometry(changed)
        for field in metadata.columns.drop("Maximum Stress (N/mm²)"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "Missing metadata"):
                    validate_geometry(metadata.drop(columns=field))

    def test_geometry_overflow_is_rejected(self):
        metadata, _ = synthetic_tables()
        metadata.loc[0, "Width (mm)"] = np.finfo(float).max
        with self.assertRaisesRegex(ValueError, "Calculated original area must be finite"):
            validate_geometry(metadata)

    def test_incorrect_area_and_peak_are_reported(self):
        for field, value, expected_check in (
            ("Area (mm²)", 21.0, "geometry"),
            ("Maximum Stress (N/mm²)", 26.0, "peak_comparison"),
            ("Maximum Stress (N/mm²)", np.nan, "peak_comparison"),
        ):
            with self.subTest(field=field, value=value):
                metadata, measurements = synthetic_tables()
                corrupted_metadata = metadata.copy(deep=True)
                corrupted_metadata.loc[0, field] = value
                report, derived = review_tables(corrupted_metadata, measurements)
                self.assertIsNone(derived)
                self.assertEqual(report["status"], "fail")
                self.assertTrue(any(item["name"] == expected_check and item["status"] == "fail" for item in report["checks"]))

    def test_missing_reported_peak_is_reported(self):
        metadata, measurements = synthetic_tables()
        report, derived = review_tables(metadata.drop(columns="Maximum Stress (N/mm²)"), measurements)
        self.assertIsNone(derived)
        self.assertEqual(report["status"], "fail")
        self.assertIn("Missing metadata", report["checks"][-1]["message"])

    def test_plot_rejects_altered_or_missing_stress_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            for filename in ("altered_stress.csv", "valid_measurements.csv"):
                with self.subTest(filename=filename):
                    _, data = synthetic_tables(filename)
                    with self.assertRaises(ValueError):
                        plot_review(data, 20.0, tmp, "synthetic", "Synthetic test data")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_geometry_and_peak_rounding_tolerances(self):
        metadata, data = synthetic_tables()
        metadata.loc[0, "Area (mm²)"] += 0.00004
        metadata.loc[0, "Maximum Stress (N/mm²)"] += 0.04
        report, derived = review_tables(metadata, data)
        self.assertIsNotNone(derived)
        self.assertNotEqual(report["status"], "fail")

    def test_fractional_record_identifier_is_preserved_and_flagged(self):
        metadata, data = synthetic_tables()
        data["Index"] = [0.0, 1.5]
        report, derived = review_tables(metadata, data)
        self.assertEqual(report["peak"]["source_index"], 1.5)
        self.assertTrue(any(warning["code"] == "record_identifiers" for warning in report["warnings"]))
        pd.testing.assert_series_equal(derived["Index"], data["Index"])

    def test_failed_workbook_emits_report_and_no_new_artifacts(self):
        metadata, measurements = synthetic_tables("missing_load.csv")
        with tempfile.TemporaryDirectory() as tmp:
            workbook = Path(tmp) / "synthetic.xlsx"
            output = Path(tmp) / "review"
            write_workbook(workbook, metadata, measurements)
            report = run_review(workbook, output)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["artifacts"], [])
            self.assertEqual({path.suffix for path in output.iterdir()}, {".md", ".json"})
            self.assertIn("not_run", (output / "synthetic_review.md").read_text())

    def test_synthetic_second_workbook_exports_without_false_attribution(self):
        metadata, measurements = synthetic_tables()
        with tempfile.TemporaryDirectory() as tmp:
            workbook = Path(tmp) / "synthetic.v2.xlsx"
            output = Path(tmp) / "output"
            write_workbook(workbook, metadata, measurements)
            report = run_review(workbook, output)
            self.assertEqual(report["status"], "pass_with_warnings")
            self.assertEqual(report["input"]["checksum_status"], "not_checked")
            self.assertNotIn("source_attribution", report)
            self.assertEqual(len(report["artifacts"]), 3)
            text = (output / "synthetic.v2_review.md").read_text()
            self.assertIn("25.0000", text)
            self.assertNotIn("FAIR Train", text)

    def test_missing_or_malformed_workbook_emits_failure_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, contents in (("missing.xlsx", None), ("malformed.xlsx", b"not a workbook")):
                with self.subTest(name=name):
                    path = Path(tmp) / name
                    if contents is not None:
                        path.write_bytes(contents)
                    report = run_review(path, Path(tmp) / "output")
                    self.assertEqual(report["status"], "fail")
                    self.assertEqual(report["artifacts"], [])
                    self.assertTrue((Path(tmp) / "output" / f"{path.stem}_review.json").is_file())

    def test_checksum_mismatch_prevents_artifact_export(self):
        metadata, measurements = synthetic_tables()
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            raw.mkdir()
            workbook = raw / "synthetic.xlsx"
            write_workbook(workbook, metadata, measurements)
            (raw / "SHA256SUMS").write_text("0" * 64 + "  synthetic.xlsx\n")
            with patch("scripts.review.DEFAULT_WORKBOOK", workbook):
                report = run_review(workbook, Path(tmp) / "output")
            self.assertEqual(report["input"]["checksum_status"], "fail")
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["artifacts"], [])

    def test_output_directory_cannot_be_input_directory(self):
        with self.assertRaisesRegex(ValueError, "separate"):
            run_review(DEFAULT_WORKBOOK, DEFAULT_WORKBOOK.parent)

    def test_export_failure_is_reported_without_publishing_staged_csv(self):
        metadata, measurements = synthetic_tables()
        with tempfile.TemporaryDirectory() as tmp:
            workbook = Path(tmp) / "synthetic.xlsx"
            output = Path(tmp) / "output"
            write_workbook(workbook, metadata, measurements)
            with patch("scripts.review.plot_review", side_effect=OSError("simulated export failure")):
                report = run_review(workbook, output)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["artifacts"], [])
            self.assertFalse((output / "synthetic_engineering_stress.csv").exists())
            self.assertIn("simulated export failure", (output / "synthetic_review.md").read_text())


class ExperimentalIntegrationTests(unittest.TestCase):
    def test_second_experimental_specimen_and_provenance(self):
        workbook = DEFAULT_WORKBOOK.parent / "4130_run_280.xlsx"
        before = workbook.read_bytes()
        self.assertEqual(hashlib.sha256(before).hexdigest(),
                         "85a59c323532dfda4cb4288e32449b706ac00dad57d1479e88aaadc0a38ecc33")
        with tempfile.TemporaryDirectory() as tmp:
            report = run_review(workbook, tmp)
            self.assertEqual(report["status"], "pass_with_warnings")
            self.assertEqual(report["input"]["checksum_status"], "pass")
            self.assertIn("FAIR Train", report["source_attribution"])
            self.assertEqual(report["row_count"], 7438)
            self.assertAlmostEqual(report["geometry"]["calculated_area_mm2"], 43.2)
            self.assertAlmostEqual(report["peak"]["calculated_stress_mpa"], 486.1631944444444)
            self.assertEqual(report["peak"]["source_index"], 5797)
            self.assertEqual(report["negative_readings"], {
                "Load (N)": 1, "Crosshead (mm)": 24, "Extensometer (mm)": 72,
            })
            exported = pd.read_csv(Path(tmp) / "4130_run_280_engineering_stress.csv")
            original = pd.read_excel(workbook, sheet_name="Sheet2", header=1, engine="openpyxl")
            pd.testing.assert_frame_equal(exported.loc[:, original.columns], original, check_exact=True)
            self.assertEqual(len(report["artifacts"]), 3)
            for artifact in report["artifacts"]:
                content = (Path(tmp) / artifact["filename"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])
        self.assertEqual(workbook.read_bytes(), before)

    def test_bundled_workbook_cli_and_artifacts(self):
        before = DEFAULT_WORKBOOK.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "-m", "scripts.review", "--output-dir", tmp],
                                    cwd=DEFAULT_WORKBOOK.parents[2], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((Path(tmp) / "1018_run_276_review.json").read_text())
            self.assertEqual(report["status"], "pass_with_warnings")
            self.assertEqual(report["input"]["checksum_status"], "pass")
            self.assertEqual(report["row_count"], 4668)
            self.assertAlmostEqual(report["geometry"]["calculated_area_mm2"], 42.7548, places=8)
            self.assertAlmostEqual(report["peak"]["calculated_stress_mpa"], 405.3774097440521, places=8)
            self.assertEqual(report["peak"]["source_index"], 3322)
            self.assertEqual(report["negative_readings"]["Load (N)"], 57)
            self.assertEqual(report["negative_readings"]["Extensometer (mm)"], 23)
            data = pd.read_csv(Path(tmp) / "1018_run_276_engineering_stress.csv")
            raw = pd.read_excel(DEFAULT_WORKBOOK, sheet_name="Sheet2", header=1, engine="openpyxl")
            pd.testing.assert_frame_equal(data.loc[:, raw.columns], raw, check_exact=True)
            validate_stress(data, report["geometry"]["calculated_area_mm2"])
            self.assertEqual(len(report["artifacts"]), 3)
            for artifact in report["artifacts"]:
                content = (Path(tmp) / artifact["filename"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])
                if artifact["filename"].endswith(".png"):
                    self.assertTrue(content.startswith(b"\x89PNG"))
                if artifact["filename"].endswith(".pdf"):
                    self.assertTrue(content.startswith(b"%PDF"))
                    self.assertNotIn(b"/CreationDate", content)
            self.assertIn("405.3774", (Path(tmp) / "1018_run_276_review.md").read_text())
        self.assertEqual(DEFAULT_WORKBOOK.read_bytes(), before)

    def test_cli_returns_nonzero_on_failed_review(self):
        metadata, measurements = synthetic_tables("duplicate_time.csv")
        with tempfile.TemporaryDirectory() as tmp:
            workbook = Path(tmp) / "synthetic.xlsx"
            write_workbook(workbook, metadata, measurements)
            output = Path(tmp) / "output"
            result = subprocess.run([sys.executable, "-m", "scripts.review", str(workbook), "--output-dir", str(output)],
                                    cwd=DEFAULT_WORKBOOK.parents[2], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("Review status: fail", result.stdout)
            self.assertTrue((output / "synthetic_review.json").exists())

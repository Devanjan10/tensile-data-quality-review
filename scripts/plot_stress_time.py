"""Replot the bundled CSV after reconciling it with the source workbook."""

import argparse

import pandas as pd

if __package__:
    from .review import DEFAULT_WORKBOOK, PROJECT_ROOT, plot_review, reference_checksums, sha256, validate_geometry, validate_stress
    from .validation import validate_measurements
else:
    from review import DEFAULT_WORKBOOK, PROJECT_ROOT, plot_review, reference_checksums, sha256, validate_geometry, validate_stress
    from validation import validate_measurements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        expected_checksum = reference_checksums()[DEFAULT_WORKBOOK.name]
        if sha256(DEFAULT_WORKBOOK) != expected_checksum:
            raise ValueError("Bundled workbook checksum disagrees with SHA256SUMS.")
        metadata = pd.read_excel(DEFAULT_WORKBOOK, sheet_name="Sheet1", header=0, engine="openpyxl")
        geometry = validate_geometry(metadata)
        output_directory = PROJECT_ROOT / "outputs"
        data = pd.read_csv(output_directory / "1018_run_276_engineering_stress.csv")
        data = validate_stress(data, geometry["calculated_area_mm2"])
        raw = validate_measurements(pd.read_excel(DEFAULT_WORKBOOK, sheet_name="Sheet2", header=1, engine="openpyxl"))
        pd.testing.assert_frame_equal(data.loc[:, raw.columns], raw, check_exact=True)
        for path in plot_review(data, geometry["calculated_area_mm2"], output_directory, "1018_run_276",
                                "Source: FAIR Train, doi:10.5281/zenodo.23424130 (CC BY 4.0)"):
            print(f"Saved: {path}")
    except (OSError, ValueError, AssertionError) as exc:
        parser.exit(1, f"Plot failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

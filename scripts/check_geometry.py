from pathlib import Path
import math

import pandas as pd


project_root = Path(__file__).resolve().parents[1]
workbook_path = project_root / "data" / "raw" / "1018_run_276.xlsx"

metadata = pd.read_excel(
    workbook_path,
    sheet_name="Sheet1",
    header=0,
    engine="openpyxl",
)

if len(metadata) != 1:
    raise ValueError("Expected one specimen metadata row.")

required_fields = ["Width (mm)", "Thickness (mm)", "Area (mm²)"]
values = {}

for field in required_fields:
    if field not in metadata.columns:
        raise ValueError(f"Missing metadata field: {field}")

    value = float(metadata.at[0, field])

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be finite and positive.")

    values[field] = value

width_mm = values["Width (mm)"]
thickness_mm = values["Thickness (mm)"]
reported_area_mm2 = values["Area (mm²)"]

calculated_area_mm2 = width_mm * thickness_mm

print(f"Original width: {width_mm:.2f} mm")
print(f"Original thickness: {thickness_mm:.2f} mm")
print(f"Calculated original area: {calculated_area_mm2:.4f} mm²")
print(f"Source-reported original area: {reported_area_mm2:.4f} mm²")

if not math.isclose(
    calculated_area_mm2,
    reported_area_mm2,
    rel_tol=0.0,
    abs_tol=0.00005,
):
    raise ValueError("Calculated area disagrees with the recorded area.")

print("PASS: Original area agrees within the rounding tolerance.")

from validation import validate_measurements

measurements = pd.read_excel(
    workbook_path,
    sheet_name="Sheet2",
    header=1,
    engine="openpyxl",
)

numeric_measurements = validate_measurements(measurements)

derived = numeric_measurements.copy(deep=True)
derived["Engineering stress (MPa)"] = (
    derived["Load (N)"] / calculated_area_mm2
)

peak_row_label = derived["Engineering stress (MPa)"].idxmax()
peak_row = derived.loc[peak_row_label]
peak_stress_mpa = float(peak_row["Engineering stress (MPa)"])

reported_peak_mpa = float(metadata.at[0, "Maximum Stress (N/mm²)"])
if not math.isfinite(reported_peak_mpa) or reported_peak_mpa <= 0:
    raise ValueError("Source-reported maximum stress must be finite and positive.")

print(f"\nPeak-load record Index: {int(peak_row['Index'])}")
print(f"Peak load: {peak_row['Load (N)']:.4f} N")
print(f"Calculated peak engineering stress: {peak_stress_mpa:.4f} MPa")
print(f"Source-reported maximum stress: {reported_peak_mpa:.1f} MPa")

if not math.isclose(
    peak_stress_mpa,
    reported_peak_mpa,
    rel_tol=0.0,
    abs_tol=0.05,
):
    raise ValueError("Peak stress disagrees with the source-reported value.")

print("PASS: Peak stress agrees within the rounding tolerance.")
print("Arithmetic agreement does not establish experimental accuracy.")

output_directory = project_root / "outputs"
output_directory.mkdir(exist_ok=True)

output_path = output_directory / "1018_run_276_engineering_stress.csv"
derived.to_csv(output_path, index=False)

# Reload the export and check that the table survives the CSV round trip.
reloaded = pd.read_csv(output_path)
pd.testing.assert_frame_equal(derived, reloaded, check_exact=True)

print(f"\nExported: {output_path.relative_to(project_root)}")
print(f"Exported rows: {len(reloaded)}")
print("PASS: Reloaded CSV matches the derived table.")

from pathlib import Path

import pandas as pd

from validation import validate_measurements


project_root = Path(__file__).resolve().parents[1]
workbook_path = project_root / "data" / "raw" / "1018_run_276.xlsx"

measurements = pd.read_excel(
    workbook_path,
    sheet_name="Sheet2",
    header=1,
    engine="openpyxl",
)

print(f"Measurement rows: {len(measurements)}")
print(f"Measurement columns: {len(measurements.columns)}")

print("\nColumn names:")
for column in measurements.columns:
    print(f"- {column}")

print("\nFirst five measurement rows:")
print(measurements.head().to_string(index=False))

print("\nMissing values per column:")
print(measurements.isna().sum().to_string())

numeric_measurements = validate_measurements(measurements)
print("\nPASS: Required columns, row count, numerical values and time checks.")

print("\nReview flags — readings preserved:")
for column in ["Load (N)", "Extensometer (mm)"]:
    negative_count = int((numeric_measurements[column] < 0).sum())
    print(f"- {column}: {negative_count} negative readings")

print("\nThese checks do not establish experimental accuracy.")

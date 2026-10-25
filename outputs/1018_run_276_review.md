# Tensile data quality review

Status: **pass_with_warnings**

Input: `1018_run_276.xlsx`
SHA-256: `27a62add1f93fcd25b7df88812bab6dbb33d1d9856216ff37191af5d587b4504`
Checksum verification: pass
Measurement rows: 4668

## Checks

| Check | Status | Finding |
| --- | --- | --- |
| input_checksum | pass | Compared bundled input bytes with data/raw/SHA256SUMS. |
| workbook_read | pass | Read Sheet1 metadata and Sheet2 measurements (header on Excel row 2). |
| measurements | pass | Required labels, row count, finite numbers and strictly increasing time. |
| geometry | pass | Original area agrees with width × thickness within the absolute tolerance. |
| stress_calculation | pass | Calculated finite engineering stress from original area; existing stress, if present, agrees. |
| peak_comparison | pass | Peak stress agrees with the reported value within the absolute tolerance. |
| csv_round_trip | pass | Reloaded CSV exactly preserves the derived table. |
| figure_export | pass | Generated PNG and PDF from validated engineering stress. |

## Geometry

Original dimensions: 13.53 × 3.16 mm.
Calculated area: 42.7548 mm²; reported: 42.7548 mm².
Absolute area tolerance: 5e-05 mm².

## Peak engineering stress

Calculated: **405.3774 MPa**; source-reported: 405.4 MPa.
Source record Index: 3322; time: 68.374001 s; load: 17331.8301 N.
Difference: -0.022590 MPa; absolute tolerance: 0.05 MPa.

## Review warnings

- Load (N): 57 negative readings retained; contextual review needed.
- Extensometer (mm): 23 negative readings retained; contextual review needed.

## Units

- Load (N): N
- Crosshead (mm): mm
- Extensometer (mm): mm
- Time (sec): s
- Engineering stress (MPa): MPa (= N/mm²)

## Artifacts from this run

- [1018_run_276_engineering_stress.csv](1018_run_276_engineering_stress.csv) — SHA-256 `4d8f5c7359b14b778651e1addff556d99c92adb81a96aee92e3d56dbc2790326`
- [1018_run_276_stress_time.png](1018_run_276_stress_time.png) — SHA-256 `c402149dcec7e1331d2a142af5edf646494f75da50a8d49964a835bcbdd02374`
- [1018_run_276_stress_time.pdf](1018_run_276_stress_time.pdf) — SHA-256 `5363cb7e610efd9ff71c51d38d56c524b2866794b93d680a5e4de58d1191ee93`

## Method and limitations

Engineering stress = measured force / original rectangular area.

- Arithmetic agreement does not establish calibration, measurement uncertainty, experimental accuracy or standards compliance.
- Units are checked through required column labels; physical units are not independently verified.
- Negative readings are retained without smoothing, origin shifts or automatic deletion.
- No strain, modulus, yield, fracture or true-stress properties are calculated.
- This workflow supports the selected Sheet1/Sheet2 rectangular-specimen layout only.
- Area and peak comparison tolerances reflect the selected workbook's displayed precision; other workbooks require a precision review.

## Source

FAIR Train: tensile testing data, doi:10.5281/zenodo.23424130 (CC BY 4.0). See docs/DATA_SOURCE.md for creator credits and provenance.

## Software

- python: 3.12.3
- pandas: 3.1.0
- numpy: 2.5.4
- matplotlib: 3.11.2
- openpyxl: 3.1.5

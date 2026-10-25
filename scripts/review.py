"""Validate one workbook and export an auditable data-quality review.

Run from the repository root with ``python -m scripts.review``.
"""

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import shutil
import tempfile
from zipfile import BadZipFile

import numpy as np
import pandas as pd

if __package__:
    from .calculations import engineering_stress_mpa
    from .validation import validate_measurements
else:
    from calculations import engineering_stress_mpa
    from validation import validate_measurements


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOK = PROJECT_ROOT / "data/raw/1018_run_276.xlsx"
AREA_TOLERANCE_MM2 = 0.00005
PEAK_TOLERANCE_MPA = 0.05
STRESS_COLUMN = "Engineering stress (MPa)"
LIMITATIONS = [
    "Arithmetic agreement does not establish calibration, measurement uncertainty, "
    "experimental accuracy or standards compliance.",
    "Units are checked through required column labels; physical units are not independently verified.",
    "Negative readings are retained without smoothing, origin shifts or automatic deletion.",
    "No strain, modulus, yield, fracture or true-stress properties are calculated.",
    "This workflow supports the selected Sheet1/Sheet2 rectangular-specimen layout only.",
    "Area and peak comparison tolerances reflect the selected workbook's displayed precision; "
    "other workbooks require a precision review.",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reference_checksums():
    """Read the trusted, versioned checksums for all bundled specimens."""
    manifest = DEFAULT_WORKBOOK.parent / "SHA256SUMS"
    return {
        filename.lstrip("*"): digest
        for digest, filename in (
            line.split(maxsplit=1) for line in manifest.read_text().splitlines() if line.strip()
        )
    }


def validate_geometry(metadata):
    """Validate original rectangular dimensions and reconcile recorded area."""
    if len(metadata) != 1:
        raise ValueError("Expected one specimen metadata row.")
    if metadata.columns.duplicated().any():
        raise ValueError("Duplicate metadata column names are not allowed.")
    values = {}
    for field in ("Width (mm)", "Thickness (mm)", "Area (mm²)"):
        if field not in metadata.columns:
            raise ValueError(f"Missing metadata field: {field}")
        try:
            value = float(metadata.iloc[0][field])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{field} must be finite and positive.") from exc
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{field} must be finite and positive.")
        values[field] = value
    area = values["Width (mm)"] * values["Thickness (mm)"]
    if not math.isfinite(area):
        raise ValueError("Calculated original area must be finite.")
    if not math.isclose(area, values["Area (mm²)"], rel_tol=0.0, abs_tol=AREA_TOLERANCE_MM2):
        raise ValueError("Calculated area disagrees with the recorded area.")
    return {
        "width_mm": values["Width (mm)"],
        "thickness_mm": values["Thickness (mm)"],
        "calculated_area_mm2": area,
        "reported_area_mm2": values["Area (mm²)"],
        "absolute_tolerance_mm2": AREA_TOLERANCE_MM2,
    }


def validate_stress(data, area_mm2):
    """Reject an absent or altered derived-stress channel before plotting."""
    if STRESS_COLUMN not in data.columns:
        raise ValueError(f"Missing required column: {STRESS_COLUMN}")
    numeric = validate_measurements(data)
    expected = engineering_stress_mpa(numeric["Load (N)"], area_mm2)
    if not np.allclose(numeric[STRESS_COLUMN], expected, rtol=1e-12, atol=1e-12):
        raise ValueError("Engineering stress disagrees with load / original area.")
    return numeric


def new_report():
    return {
        "schema_version": 1,
        "status": "fail",
        "checks": [],
        "warnings": [],
        "artifacts": [],
        "units": {
            "Load (N)": "N", "Crosshead (mm)": "mm", "Extensometer (mm)": "mm",
            "Time (sec)": "s", STRESS_COLUMN: "MPa (= N/mm²)",
        },
        "method": "Engineering stress = measured force / original rectangular area.",
        "limitations": LIMITATIONS.copy(),
    }


def add_check(report, name, status, message):
    report["checks"].append({"name": name, "status": status, "message": message})


def finish_status(report):
    if any(check["status"] == "fail" for check in report["checks"]):
        report["status"] = "fail"
    else:
        report["status"] = "pass_with_warnings" if report["warnings"] else "pass"


def review_tables(metadata, measurements):
    """Return a report and derived table, or None when required checks fail.

    Tables are copied by validation; no source rows are removed or edited.
    """
    report = new_report()
    report["row_count"] = len(measurements)
    numeric = geometry = None
    try:
        numeric = validate_measurements(measurements)
        add_check(report, "measurements", "pass", "Required labels, row count, finite numbers and strictly increasing time.")
        report["time_range_s"] = [float(numeric["Time (sec)"].iloc[0]), float(numeric["Time (sec)"].iloc[-1])]
        report["negative_readings"] = {}
        for column in ("Load (N)", "Crosshead (mm)", "Extensometer (mm)"):
            count = int((numeric[column] < 0).sum())
            report["negative_readings"][column] = count
            if count:
                report["warnings"].append({
                    "code": "negative_readings", "column": column, "count": count,
                    "message": f"{column}: {count} negative readings retained; contextual review needed.",
                })
        identifiers = numeric["Index"]
        if identifiers.duplicated().any() or (identifiers % 1 != 0).any():
            report["warnings"].append({
                "code": "record_identifiers",
                "message": "Source Index contains duplicate or fractional identifiers; records retained.",
            })
    except (ValueError, TypeError) as exc:
        add_check(report, "measurements", "fail", str(exc))
    try:
        geometry = validate_geometry(metadata)
        report["geometry"] = geometry
        add_check(report, "geometry", "pass", "Original area agrees with width × thickness within the absolute tolerance.")
    except (ValueError, TypeError) as exc:
        add_check(report, "geometry", "fail", str(exc))

    derived = None
    if numeric is None or geometry is None:
        add_check(report, "stress_calculation", "not_run", "Requires valid measurements and geometry.")
        add_check(report, "peak_comparison", "not_run", "Requires calculated engineering stress.")
    else:
        try:
            if STRESS_COLUMN in numeric.columns:
                validate_stress(numeric, geometry["calculated_area_mm2"])
            derived = numeric.copy(deep=True)
            derived[STRESS_COLUMN] = engineering_stress_mpa(derived["Load (N)"], geometry["calculated_area_mm2"])
            add_check(report, "stress_calculation", "pass", "Calculated finite engineering stress from original area; existing stress, if present, agrees.")
        except (ValueError, TypeError) as exc:
            add_check(report, "stress_calculation", "fail", str(exc))
        if derived is None:
            add_check(report, "peak_comparison", "not_run", "Requires valid engineering stress.")
        else:
            try:
                field = "Maximum Stress (N/mm²)"
                if field not in metadata.columns:
                    raise ValueError(f"Missing metadata field: {field}")
                reported = float(metadata.iloc[0][field])
                if not math.isfinite(reported) or reported <= 0:
                    raise ValueError("Source-reported maximum stress must be finite and positive.")
                position = int(np.argmax(derived[STRESS_COLUMN].to_numpy()))
                peak = float(derived[STRESS_COLUMN].iloc[position])
                record_index = derived["Index"].iloc[position]
                report["peak"] = {
                    "source_index": record_index.item() if hasattr(record_index, "item") else record_index,
                    "time_s": float(derived["Time (sec)"].iloc[position]),
                    "load_n": float(derived["Load (N)"].iloc[position]),
                    "calculated_stress_mpa": peak, "reported_stress_mpa": reported,
                    "difference_mpa": peak - reported, "absolute_tolerance_mpa": PEAK_TOLERANCE_MPA,
                }
                if not math.isclose(peak, reported, rel_tol=0.0, abs_tol=PEAK_TOLERANCE_MPA):
                    raise ValueError("Peak stress disagrees with the source-reported value.")
                add_check(report, "peak_comparison", "pass", "Peak stress agrees with the reported value within the absolute tolerance.")
            except (ValueError, TypeError) as exc:
                add_check(report, "peak_comparison", "fail", str(exc))
    finish_status(report)
    return report, derived if report["status"] != "fail" else None


def plot_review(data, area_mm2, output_directory, stem, source_note):
    """Plot only a validated stress channel; return generated paths."""
    data = validate_stress(data, area_mm2)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    position = int(np.argmax(data[STRESS_COLUMN].to_numpy()))
    peak_time = data["Time (sec)"].iloc[position]
    peak_stress = data[STRESS_COLUMN].iloc[position]
    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        ax.plot(data["Time (sec)"], data[STRESS_COLUMN], linewidth=1.3, label=f"All {len(data):,} recorded points")
        ax.scatter([peak_time], [peak_stress], color="darkred", s=35, zorder=3,
                   label=f"Peak engineering stress: {peak_stress:.2f} MPa")
        ax.set(xlabel="Recorded time (s)", ylabel="Engineering stress (MPa)", title=stem.replace("_", " "))
        ax.axhline(0, color="grey", linewidth=0.7)
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=9)
        fig.text(0.02, 0.02, f"{source_note}\nOriginal area: {area_mm2:.4f} mm². "
                 "Negative readings retained; no smoothing or origin shift.", fontsize=8)
        fig.tight_layout(rect=(0, 0.10, 1, 1))
        paths = []
        for extension in ("png", "pdf"):
            path = Path(output_directory) / f"{stem}_stress_time.{extension}"
            # Avoid changing artifact checksums solely because a plot was rerun.
            metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else None
            fig.savefig(path, dpi=300, metadata=metadata)
            paths.append(path)
        return paths
    finally:
        plt.close(fig)


def render_markdown(report):
    lines = ["# Tensile data quality review", "", f"Status: **{report['status']}**", ""]
    source = report.get("input", {})
    lines += [f"Input: `{source.get('filename', 'unknown')}`", f"SHA-256: `{source.get('sha256', 'unavailable')}`",
              f"Checksum verification: {source.get('checksum_status', 'not_run')}",
              f"Measurement rows: {report.get('row_count', 'unavailable')}", "", "## Checks", "",
              "| Check | Status | Finding |", "| --- | --- | --- |"]
    for check in report["checks"]:
        message = check["message"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {check['name']} | {check['status']} | {message} |")
    if "geometry" in report:
        geometry = report["geometry"]
        lines += ["", "## Geometry", "", f"Original dimensions: {geometry['width_mm']} × {geometry['thickness_mm']} mm.",
                  f"Calculated area: {geometry['calculated_area_mm2']:.4f} mm²; reported: {geometry['reported_area_mm2']:.4f} mm².",
                  f"Absolute area tolerance: {geometry['absolute_tolerance_mm2']} mm²."]
    if "peak" in report:
        peak = report["peak"]
        lines += ["", "## Peak engineering stress", "",
                  f"Calculated: **{peak['calculated_stress_mpa']:.4f} MPa**; source-reported: {peak['reported_stress_mpa']} MPa.",
                  f"Source record Index: {peak['source_index']}; time: {peak['time_s']:.6f} s; load: {peak['load_n']:.4f} N.",
                  f"Difference: {peak['difference_mpa']:.6f} MPa; absolute tolerance: {peak['absolute_tolerance_mpa']} MPa."]
    lines += ["", "## Review warnings", ""]
    lines += [f"- {warning['message']}" for warning in report["warnings"]] or ["None."]
    lines += ["", "## Units", ""] + [f"- {label}: {unit}" for label, unit in report["units"].items()]
    lines += ["", "## Artifacts from this run", ""]
    lines += [f"- [{item['filename']}]({item['filename']}) — SHA-256 `{item['sha256']}`" for item in report["artifacts"]] or ["None; failed runs do not export new derived data or figures."]
    lines += ["", "## Method and limitations", "", report["method"], ""]
    lines += [f"- {item}" for item in report["limitations"]]
    if report.get("source_attribution"):
        lines += ["", "## Source", "", report["source_attribution"]]
    lines += ["", "## Software", ""] + [f"- {name}: {version}" for name, version in report.get("software", {}).items()]
    return "\n".join(lines) + "\n"


def run_review(workbook_path=DEFAULT_WORKBOOK, output_directory=None):
    """Write JSON/Markdown reports even on validation failure. Return the report."""
    workbook_path = Path(workbook_path).resolve()
    output_directory = Path(output_directory) if output_directory is not None else PROJECT_ROOT / "outputs"
    output_directory = output_directory.resolve()
    # Never allow derived artifacts to overwrite the raw-data directory.
    raw_directory = DEFAULT_WORKBOOK.parent.resolve()
    if output_directory == raw_directory or raw_directory in output_directory.parents or output_directory == workbook_path.parent:
        raise ValueError("Output directory must be separate from the input/raw-data directory.")
    output_directory.mkdir(parents=True, exist_ok=True)
    report = new_report()
    derived = None
    input_info = {"filename": workbook_path.name, "sha256": None, "checksum_status": "not_checked"}
    input_checks = []
    try:
        input_info["sha256"] = sha256(workbook_path)
        references = reference_checksums()
        expected = references.get(workbook_path.name)
        is_bundled = workbook_path.parent == raw_directory and expected is not None
        known_content = input_info["sha256"] in references.values()
        if is_bundled or known_content:
            matches = input_info["sha256"] == expected if is_bundled else known_content
            input_info["checksum_status"] = "pass" if matches else "fail"
            input_checks.append({"name": "input_checksum", "status": input_info["checksum_status"],
                                 "message": "Compared bundled input bytes with data/raw/SHA256SUMS."})
        if known_content:
            report["source_attribution"] = "FAIR Train: tensile testing data, doi:10.5281/zenodo.23424130 (CC BY 4.0). See docs/DATA_SOURCE.md for creator credits and provenance."
        with pd.ExcelFile(workbook_path, engine="openpyxl") as workbook:
            metadata = pd.read_excel(workbook, sheet_name="Sheet1", header=0)
            measurements = pd.read_excel(workbook, sheet_name="Sheet2", header=1)
        source_attribution = report.get("source_attribution")
        report, derived = review_tables(metadata, measurements)
        if source_attribution:
            report["source_attribution"] = source_attribution
        input_checks.append({"name": "workbook_read", "status": "pass", "message": "Read Sheet1 metadata and Sheet2 measurements (header on Excel row 2)."})
    except (OSError, ValueError, TypeError, KeyError, BadZipFile) as exc:
        input_checks.append({"name": "workbook_read", "status": "fail", "message": str(exc)})
    report["input"] = input_info
    report["checks"] = input_checks + report["checks"]
    report["software"] = {"python": platform.python_version(), **{
        name: importlib.metadata.version(name) for name in ("pandas", "numpy", "matplotlib", "openpyxl")
    }}
    if input_info["checksum_status"] == "not_checked":
        report["warnings"].append({"code": "unverified_input",
                                    "message": "Input SHA-256 recorded; no trusted checksum comparison performed for this path."})
    finish_status(report)
    if derived is not None and report["status"] != "fail":
        try:
            with tempfile.TemporaryDirectory(prefix=".review-", dir=output_directory) as tmp:
                staging = Path(tmp)
                csv_path = staging / f"{workbook_path.stem}_engineering_stress.csv"
                derived.to_csv(csv_path, index=False)
                reloaded = pd.read_csv(csv_path)
                pd.testing.assert_frame_equal(derived.reset_index(drop=True), reloaded, check_exact=True)
                add_check(report, "csv_round_trip", "pass", "Reloaded CSV exactly preserves the derived table.")
                paths = [csv_path] + plot_review(reloaded, report["geometry"]["calculated_area_mm2"], staging, workbook_path.stem,
                    "Source: FAIR Train, doi:10.5281/zenodo.23424130 (CC BY 4.0)" if report.get("source_attribution") else f"Input: {workbook_path.name}; source provenance not independently verified.")
                for path in paths:
                    shutil.copyfile(path, output_directory / path.name)
                    report["artifacts"].append({"filename": path.name, "sha256": sha256(path)})
                add_check(report, "figure_export", "pass", "Generated PNG and PDF from validated engineering stress.")
        except (OSError, ValueError, AssertionError, TypeError) as exc:
            add_check(report, "artifact_export", "fail", str(exc))
            report["artifacts"] = []
    else:
        add_check(report, "artifact_export", "not_run", "Validation failed; no new derived data or figures exported.")
    finish_status(report)
    json_path = output_directory / f"{workbook_path.stem}_review.json"
    markdown_path = output_directory / f"{workbook_path.stem}_review.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "outputs")
    args = parser.parse_args(argv)
    try:
        report = run_review(args.workbook, args.output_dir)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Review failed: {exc}\n")
    print(f"Review status: {report['status']}")
    for check in report["checks"]:
        print(f"{check['status'].upper()}: {check['name']} — {check['message']}")
    for warning in report["warnings"]:
        print(f"WARNING: {warning['message']}")
    print(f"Reports: {args.output_dir.resolve() / (args.workbook.stem + '_review')}.[md,json]")
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

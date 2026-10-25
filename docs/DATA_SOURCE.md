# Data source and attribution

- Dataset: FAIR Train: tensile testing data, version 2.
- Source: https://zenodo.org/records/23424130
- DOI: https://doi.org/10.5281/zenodo.23424130
- Published: 2026-10-16.
- License recorded by Zenodo: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ .
- Creators, as listed in the record: Brian, Schuster; Erwin, Cazares; Edgar, Tarin; Wodo, Olga.
- The upstream README credits Edgar Tarin for core functions (MASE6401, UTEP, 2025-10-20), Brian Schuster for course delivery, and Olga Wodo for code/folder organization. A verbatim copy is retained in `upstream/README_original.txt`.

## Selected input

Archive supplied by the project learner: `TensileTestProject.zip`.

Archive SHA-256: `96ae93522f7c8c21d26d794f4b92dc0181178d32ad2ebcf7b331142df16a1235`.

Original archive member:

```text
TensileTestProject/data/dataClass2025/rawData/1018_Crosshead_Extensometer_displacement_S20 50mm Gage Length ASTM E8 Metals Tension (Extensometer-Crosshead) 276- Test Run 1-Test Run 1-Crosshead data.xlsx
```

Project path: `data/raw/1018_run_276.xlsx`.

Workbook SHA-256: `27a62add1f93fcd25b7df88812bab6dbb33d1d9856216ff37191af5d587b4504`.

Change: shortened filename only; workbook bytes unchanged. This workbook is experimental source data, not a measurement performed by the portfolio author.

The upstream README mentions CSV files and sheets; the actual selected file is an Excel `.xlsx` workbook. Do not use the CSV prototype's parser for it.

## Second input: 4130 steel, run 280

The second specimen was extracted byte-for-byte from the same learner-supplied
archive. The archive SHA-256 was rechecked against the value above before
extraction. No upstream analysis code was copied.

Original archive member:

```text
TensileTestProject/data/dataClass2025/rawData/4130_2_Crosshead_Extensometer_displacement_S20 50mm Gage Length ASTM E8 Metals Tension (Extensometer-Crosshead) 280- Test Run 1-Test Run 1-Crosshead data.xlsx
```

Project path: `data/raw/4130_run_280.xlsx`.

Workbook SHA-256: `85a59c323532dfda4cb4288e32449b706ac00dad57d1479e88aaadc0a38ecc33`.

Change: shortened filename only; workbook bytes unchanged. The dataset credits,
reuse terms and scientific limitations above apply to both inputs. Both
checksums are recorded in `data/raw/SHA256SUMS`.

## Initial inspection notes, to reproduce locally

- Sheet1 contains specimen metadata and source-reported results.
- Sheet2 contains measurements with headers on Excel row 2.
- Sheet3 is empty in this selected workbook.
- Load, crosshead displacement and extensometer readings are separate channels.

These notes were recorded during initial inspection. The current read-only
inspection script is `python -m scripts.inspect_workbook`; the implemented
validation and report workflow is `python -m scripts.review`. Source-reported
properties remain separate from derived results. See the generated review for
the current check outcomes and their limits.

## Scientific limits

A source filename mentioning a standard does not establish compliance. The marked gauge length does not by itself confirm the installed extensometer reference length. Calibration, measurement uncertainty, test setup and preprocessing assumptions need separate evidence.

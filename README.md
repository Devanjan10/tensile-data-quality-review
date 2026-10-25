# Tensile Data Quality Review

A student portfolio project on reproducible processing and quality assessment of experimental tensile-test data using Python.

## Current status

Repository setup only. The first real workbook and its attribution are included. No analysis program has been implemented in this repository yet. No experimental accuracy or standards compliance has been established.

## First question

Can we reproduce the selected specimen's reported peak engineering stress from the original load measurements and original cross-section, while preserving records and identifying information needed for further analysis?

Engineering stress: sigma = F / A0. With force in N and area in mm², stress is N/mm² = MPa.

Strain calculations will require a confirmed measurement channel and reference length. Crosshead displacement will not silently replace specimen gauge extension.

## Input

`data/raw/1018_run_276.xlsx` is an unchanged workbook from FAIR Train: tensile testing data, Zenodo record 23424130. Only its filename was shortened. The original archive contains 11 raw workbooks; this first milestone includes one.

See [source attribution](docs/DATA_SOURCE.md) for the DOI, author credits, reuse terms, original path and checksums. The workbook includes source-reported properties; they are reference values, not results calculated by this project.

## Planned workflow

1. Inspect workbook sheets, headers and specimen metadata.
2. Check file structure, numerical values and declared units.
3. Reconcile area and peak engineering stress independently.
4. Preserve raw records and document review flags.
5. Export derived data, figures and a short methods/findings/limitations report.
6. Evaluate checks using separately labeled error-injected copies.

Do not automatically delete negative readings, smooth curves, shift origins or remove outliers.

## Project folders

- `data/raw/`: attributed, unchanged experimental input and checksum.
- `docs/`: source notes, scope and development log.
- `scripts/`: analysis code to be added incrementally.
- `tests/`: numerical and validation tests to be added with the code.
- `outputs/`: generated results; currently empty.

## Reproducibility

A Python virtual environment, requirements file, executable commands and tests will be added in subsequent milestones. There is no analysis command to run yet.

To check the bundled input bytes on Ubuntu:

```bash
cd data/raw
sha256sum -c SHA256SUMS
```

## Scope and limitations

This work will assess data consistency and calculation reproducibility. Software checks alone cannot establish instrument calibration, measurement uncertainty, experimental accuracy or compliance with a test standard. Yield strength, modulus, fracture properties and true-stress calculations are outside the first milestone.

## Development record

See [progress](docs/PROGRESS.md). This is a learning project supported by an AI assistant. The initial structure and documentation were prepared with assistance. Later entries should state what was implemented, understood and independently verified. No client experience, measured time savings or paid demand is claimed.

## Data reuse

The source dataset is published under CC BY 4.0. Its terms and attribution remain separate from any future license selected for original project code. Upstream analysis scripts have not been copied into the project's implementation.

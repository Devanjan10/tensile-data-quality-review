# First specimen analysis: 1018, run 276

## Question
Can the original load measurements and recorded original dimensions
reproduce the workbook's reported maximum engineering stress?

## Method and findings
- Imported all 4,668 measurement rows.
- Original rectangular dimensions: 13.53 mm × 3.16 mm.
- Calculated original area: 42.7548 mm²; agrees with recorded area.
- Engineering stress calculated as load in N divided by original area
  in mm², giving MPa.
- Peak engineering stress: 405.3774 MPa at source record Index 3322.
- Source-reported maximum stress: 405.4 MPa.
- Agreement checked against a rounding tolerance of 0.05 MPa.
- Retained all negative measurements without smoothing or origin shifts.
- Exported a derived CSV and checked exact equality after reloading.
- Generated engineering-stress-versus-recorded-time PNG and PDF figures.

## Verification scope
The automated suite now covers hand-checkable stress calculations, invalid
and overflowing dimensions, missing fields, short measurement tables,
nonfinite readings, repeated/decreasing timestamps (including unsigned
integers), altered derived stress, area/peak disagreements, record-identifier
preservation, failed-review reports and CLI exit codes.

Separately labeled synthetic fixtures are stored in `tests/fixtures/`.
They are not experimental measurements. An integration test runs the full
pipeline against the bundled workbook, verifies its known peak and row count,
compares exported source measurements exactly and checks artifact hashes.
A synthetic workbook checks filename handling and prevents false source
attribution. A second experimental specimen has also been verified, as
described below.

Run `python -m unittest discover -v` and `python -m scripts.review` from
the repository root. Generated Markdown and JSON reports identify the
input checksum, software versions, checks, warnings and artifacts.

The bundled input checksum must match `data/raw/SHA256SUMS`. Negative
readings are warnings and remain in the output. Failed validation returns
exit code 1 and writes a failure report without new derived-data or figure
exports. Earlier artifacts can remain; consult the latest report's artifact
list or use a fresh output directory.

The area tolerance is 0.00005 mm² and the peak tolerance is 0.05 MPa,
with zero relative tolerance for both. These tolerances reflect the
selected source's displayed precision and require review for other inputs.
Stress consistency before plotting uses relative and absolute tolerances
of 1e-12. Physical units are inferred from column labels, not independently
verified. Numerical checks do not replace scientific interpretation.

## Second specimen: 4130 steel, run 280

The same workflow was run on a second unchanged workbook from the documented
archive. All 7,438 measurement rows were imported and preserved. Dimensions
13.5 × 3.2 mm give an original area of 43.2 mm². The calculated peak is
486.1631944444444 MPa at source Index 5797, agreeing with the reported
486.2 MPa within 0.05 MPa. This reference has the same one-decimal stress
precision as the first specimen, so the existing peak tolerance applies.
The area calculation agrees exactly with its recorded area; the existing
area tolerance is conservative for this input's displayed precision.

The review retains and flags 1 negative load reading, 24 negative crosshead
readings and 72 negative extensometer readings. An integration test checks
the expected result, checksum, row preservation and generated artifact hashes.
See `outputs/4130_run_280_review.md` and `docs/DATA_SOURCE.md`.

## Limitations
Arithmetic agreement does not establish calibration, measurement
uncertainty, experimental accuracy or compliance with a test standard.
Negative readings and abrupt changes require contextual review.
No strain, modulus, yield or fracture-property calculation is claimed.

## Source
FAIR Train: tensile testing data, DOI 10.5281/zenodo.23424130.
See DATA_SOURCE.md for attribution, reuse terms and input provenance.

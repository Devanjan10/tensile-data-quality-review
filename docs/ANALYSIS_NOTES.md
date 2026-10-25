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
Four automated tests cover selected measurement-validation behaviours.
Geometry and peak stress were checked against workbook reference values.
Dedicated automated tests for geometry and stress calculations remain
to be added. Figure generation succeeded; visual review remains pending.

## Limitations
Arithmetic agreement does not establish calibration, measurement
uncertainty, experimental accuracy or compliance with a test standard.
Negative readings and abrupt changes require contextual review.
No strain, modulus, yield or fracture-property calculation is claimed.

## Source
FAIR Train: tensile testing data, DOI 10.5281/zenodo.23424130.
See DATA_SOURCE.md for attribution, reuse terms and input provenance.

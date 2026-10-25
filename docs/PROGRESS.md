# Development log

## Milestone 0 — project setup

Prepared with AI assistance:

- A separate project structure.
- One byte-identical raw workbook selected from the supplied archive.
- Source attribution, file checksums and an initial analysis question.
- Ignore rules for environments, caches, credentials and generated outputs.

Pending learner checks:

- [ ] Initialize the local repository on `main`.
- [ ] Review the source attribution and README.
- [ ] Verify the workbook checksum.
- [ ] Create the first local commit.
- [ ] Create the GitHub repository and push the setup.

No analysis code has been added. No client work or experimental certification is claimed.

## Next milestones

1. Create the virtual environment and record dependencies.
2. Implement a read-only Excel inspection script; review its output.
3. Implement dimensional and numerical checks and peak-stress reconciliation.
4. Add appropriate numerical tests and separately labeled corrupted fixtures.
5. Export figures, derived data and a per-file quality-review report.
6. Prepare a short case study and demonstration video.

For each milestone, record what changed, what was checked, the result, unresolved questions and who performed the verification. Commit messages should describe actual changes; Git history records development, not scientific accuracy by itself.

## Milestone 1 — workbook inspection and measurement import

Implemented and run locally with AI guidance:

- Listed workbook sheets and previewed their contents.
- Identified Sheet1 as metadata and source-reported results.
- Identified Excel row 2 as the measurement header in Sheet2.
- Loaded 4,668 measurement rows and five columns.
- Checked for missing entries: Pandas reported zero in each column.
- Preserved the original experimental workbook.

These checks establish successful import, not experimental accuracy.
Numerical validity, timestamps, specimen metadata and calculations
remain to be checked.

## Milestone 2 — reusable measurement validation

- Connected the experimental-data reader to a reusable validation function.
- The 4,668-row workbook passed the implemented column, row-count,
  numerical-finiteness and strictly increasing time checks.
- Preserved 57 negative load readings and 23 negative extensometer readings.
- Four automated tests passed, covering preservation of finite negative
  readings, repeated timestamps, nonfinite values and nonnumeric load text.
- Confirmed that the original workbook checksum remains unchanged.

Coverage limitations: missing-column, too-short-table and decreasing-time
cases have not yet been tested independently. Plausible numerical errors,
incorrect physical units and experimental accuracy are not established
by these tests.

## Milestone 3 — automated review workflow (2026-10-25)

Implemented with AI assistance:

- Reused the existing engineering-stress helper in a single-command workbook
  review, including geometry reconciliation, peak comparison, CSV export,
  figures and Markdown/JSON review reports.
- Fixed unsigned timestamp subtraction overflow and added duplicate-column
  rejection. Fractional or duplicate source record identifiers are preserved
  with warnings.
- Added original-area and source-measurement checks before replotting the
  bundled CSV, preventing altered finite stress from silently reaching figures.
- Added labeled synthetic error-injected fixtures and expanded validation,
  geometry, numerical and integration tests. Default unittest discovery now
  finds the test suite.
- Added input/artifact checksums, recorded software versions and explicit
  per-check outcomes, warnings, limitations and failure exit codes.
- Replaced outdated setup instructions with reproducible commands and
  configured GitHub Actions for tests, checksum verification and review artifacts.

Verification: run the documented suite and review command to reproduce the
local checks. The experimental integration test asserts 4,668 records, an
original area of 42.7548 mm², peak 405.3774097440521 MPa at Index 3322,
preserved negative readings and unchanged workbook bytes. Remote CI execution
has not been confirmed by this local implementation.

Remaining: independently review the generated report and figure; validate a
second experimental specimen with documented provenance; assess additional
domain checks using experimental context. No strain or additional mechanical
properties have been added.

## Milestone 4 — second specimen and publication (2026-10-25)

- Located the original learner-supplied archive locally and verified its
  documented SHA-256 before selecting 4130 steel run 280.
- Extracted the second workbook without changing its bytes; recorded its
  original archive member, shortened filename and checksum in DATA_SOURCE.md.
- Extended checksum verification and source attribution to both versioned
  inputs, including fail-closed checks for altered bundled workbooks.
- Verified all 7,438 rows, 43.2 mm² original area and peak 486.1631944444444 MPa
  at source Index 5797 against the reported 486.2 MPa. Preserved and flagged
  1 negative load, 24 negative crosshead and 72 negative extensometer readings.
- Generated the second specimen's CSV, Markdown/JSON reports and PNG/PDF
  figures. The assistant inspected the figures for readable labels and layout;
  independent scientific interpretation remains outside this software review.
- Added a second experimental integration test. All 32 tests pass locally,
  including in a fresh dependency environment with host Python paths excluded.
- Configured CI to check dependencies and both input checksums, run the entire
  suite, generate both specimen reviews and retain the outputs as an artifact.
  The README badge links to the published workflow results.

The implementation is ready for versioned publication. Calibration,
uncertainty, standards compliance and additional mechanical properties remain
outside the completed milestone's scope.

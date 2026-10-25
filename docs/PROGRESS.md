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

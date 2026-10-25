# Synthetic fixtures — not experimental measurements

All values here are hand-checkable test inputs. No workbook in `data/raw/`
was changed to create them. The original area is 10 × 2 = 20 mm²;
the expected stresses are −0.1 and 25 MPa.

| Fixture | Injected fault | Expected finding |
| --- | --- | --- |
| valid_measurements.csv + metadata.json | None | Pass with negative-reading warnings |
| missing_load.csv | Removed second load | Measurement validation fails |
| duplicate_time.csv | Repeated timestamp | Measurement validation fails |
| altered_stress.csv | Stress multiplied by 1,000 | Stress consistency fails |

`test_review.py` also creates separately named in-memory copies for missing
metadata, invalid dimensions, incorrect recorded area and incorrect reported
peak. Tests write synthetic workbooks only in temporary directories, using
the same Sheet1/Sheet2 header layout as the selected experimental workbook.

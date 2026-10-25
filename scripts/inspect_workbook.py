from pathlib import Path

import pandas as pd


project_root = Path(__file__).resolve().parents[1]
workbook_path = project_root / "data" / "raw" / "1018_run_276.xlsx"

with pd.ExcelFile(workbook_path, engine="openpyxl") as workbook:
    print(f"Workbook: {workbook_path.name}")
    print(f"Number of sheets: {len(workbook.sheet_names)}")

    for sheet_name in workbook.sheet_names:
        print(f"- {sheet_name}")

    for sheet_name in workbook.sheet_names:
        print(f"\n--- Preview: {sheet_name} ---")

        preview = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            header=None,
            nrows=4,
        )

        if preview.empty:
            print("This sheet contains no tabular data.")
        else:
            print(preview.to_string(index=False, header=False))

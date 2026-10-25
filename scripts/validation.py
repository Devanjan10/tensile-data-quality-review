import numpy as np
import pandas as pd


def validate_measurements(measurements):
    """Check table structure, numerical values and increasing time."""
    required = {
        "Index", "Load (N)", "Crosshead (mm)",
        "Extensometer (mm)", "Time (sec)",
    }

    if measurements.columns.duplicated().any():
        raise ValueError("Duplicate column names are not allowed.")

    missing = required - set(measurements.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if len(measurements) < 2:
        raise ValueError("At least two measurement rows are required.")

    numeric = measurements.apply(pd.to_numeric, errors="raise")

    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Missing or infinite numerical values.")

    times = numeric["Time (sec)"].to_numpy()
    # Compare directly: subtraction can wrap for unsigned timestamps.
    if not (times[1:] > times[:-1]).all():
        raise ValueError("Time must increase strictly.")

    return numeric

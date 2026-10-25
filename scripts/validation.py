import numpy as np
import pandas as pd


def validate_measurements(measurements):
    """Check table structure, numerical values and increasing time."""
    required = {
        "Index", "Load (N)", "Crosshead (mm)",
        "Extensometer (mm)", "Time (sec)",
    }

    missing = required - set(measurements.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if len(measurements) < 2:
        raise ValueError("At least two measurement rows are required.")

    numeric = measurements.apply(pd.to_numeric, errors="raise")

    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Missing or infinite numerical values.")

    time_steps = np.diff(numeric["Time (sec)"].to_numpy())
    if not (time_steps > 0).all():
        raise ValueError("Time must increase strictly.")

    return numeric

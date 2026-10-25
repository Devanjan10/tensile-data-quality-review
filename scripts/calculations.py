import numpy as np


def engineering_stress_mpa(force_n, area_mm2):
    """Calculate engineering stress from force in N and original area in mm²."""
    area_mm2 = float(area_mm2)

    if not np.isfinite(area_mm2) or area_mm2 <= 0:
        raise ValueError("Original area must be finite and positive.")

    forces = np.asarray(force_n, dtype=float)

    if not np.isfinite(forces).all():
        raise ValueError("Force values must be finite.")

    stress = forces / area_mm2

    if not np.isfinite(stress).all():
        raise ValueError("Calculated stress contains nonfinite values.")

    return stress

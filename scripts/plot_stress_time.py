from pathlib import Path

import matplotlib
import pandas as pd

from validation import validate_measurements

matplotlib.use("Agg")
import matplotlib.pyplot as plt


project_root = Path(__file__).resolve().parents[1]
output_directory = project_root / "outputs"
csv_path = output_directory / "1018_run_276_engineering_stress.csv"

data = validate_measurements(pd.read_csv(csv_path))

time_s = data["Time (sec)"]
stress_mpa = data["Engineering stress (MPa)"]

peak_label = stress_mpa.idxmax()
peak_time_s = time_s.loc[peak_label]
peak_stress_mpa = stress_mpa.loc[peak_label]

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(
    time_s,
    stress_mpa,
    linewidth=1.3,
    label=f"All {len(data):,} recorded points",
)

ax.scatter(
    [peak_time_s],
    [peak_stress_mpa],
    color="darkred",
    s=35,
    zorder=3,
    label=f"Peak engineering stress: {peak_stress_mpa:.2f} MPa",
)

ax.set_xlabel("Recorded time (s)")
ax.set_ylabel("Engineering stress (MPa)")
ax.set_title("1018 steel — run 276")
ax.axhline(0, color="grey", linewidth=0.7)
ax.grid(True, alpha=0.25)
ax.legend(fontsize=9)

fig.text(
    0.02,
    0.02,
    "Source: FAIR Train, doi:10.5281/zenodo.23424130 (CC BY 4.0)\n"
    "Original area: 42.7548 mm². Negative readings retained; no smoothing or origin shift.",
    fontsize=8,
)

fig.tight_layout(rect=(0, 0.10, 1, 1))

for extension in ("png", "pdf"):
    figure_path = output_directory / f"1018_run_276_stress_time.{extension}"
    fig.savefig(figure_path, dpi=300)
    print(f"Saved: {figure_path.relative_to(project_root)}")

plt.close(fig)

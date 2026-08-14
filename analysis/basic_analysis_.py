"""Basic post-processing for saved spectrum CSV files."""

from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import pandas as pd


def plot_spectrum(csv_file: Path, output_dir: Path) -> None:
    data = pd.read_csv(csv_file)

    required = {"frequency_hz", "power_dbm"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns in {csv_file}: {sorted(missing)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{csv_file.stem}_spectrum.png"

    plt.figure(figsize=(10, 5.5))
    plt.plot(data["frequency_hz"] / 1e9, data["power_dbm"], linewidth=1.2)
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Power (dBm)")
    plt.title(csv_file.stem)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved plot: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot saved spectrum analyzer CSV files."
    )
    parser.add_argument("files", nargs="+", help="CSV files to analyse")
    parser.add_argument(
        "--output",
        default="plots",
        help="Directory in which plots will be saved",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    for filename in args.files:
        plot_spectrum(Path(filename), output_dir)


if __name__ == "__main__":
    main()

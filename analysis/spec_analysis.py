import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# USER SETTINGS
# ============================================================

# Fixed H1 frequency
H1_FREQ_MHZ = 1420.4

# Plot range
START_GHZ = 1.0
STOP_GHZ = 2.0

# ============================================================
# OUTPUT FOLDER
# ============================================================

# All plots and the final summary will be saved here
OUTPUT_FOLDER = "Fss_analysis_plots"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

print("Output folder:")
print(os.path.abspath(OUTPUT_FOLDER))


# ============================================================
# ENTER YOUR FILE PAIRS HERE
#
# For every test:
#
#   rfi_mhz = actual RFI frequency used
#   no_fss  = averaged WITHOUT FSS CSV
#   with_fss = averaged WITH FSS CSV
#
# ============================================================

TESTS = [

    {
        "rfi_mhz": 1100,
        "no_fss": "/path/to/your/csv/file",
        "with_fss": "/path/to/your/csv/file"
    },

    {
        "rfi_mhz": 1200,
        "no_fss": "/path/to/your/csv/file",
        "with_fss": "/path/to/your/csv/file"
    },

    # Add additional RFI frequencies and CSV file paths as required
]

# ============================================================
# READ CSV
# ============================================================

def read_spectrum(filename):

    data = pd.read_csv(filename)

    frequency = data["Frequency_GHz"].to_numpy()

    if "Average_Power_dBm" in data.columns:

        power = data["Average_Power_dBm"].to_numpy()

    elif "Power_dBm" in data.columns:

        power = data["Power_dBm"].to_numpy()

    else:

        raise ValueError(
            f"Power column not found in {filename}"
        )

    return frequency, power


# ============================================================
# RESULTS
# ============================================================

results = []


# ============================================================
# PROCESS EACH TEST
# ============================================================

for test in TESTS:

    rfi_mhz = test["rfi_mhz"]

    no_file = test["no_fss"]

    fss_file = test["with_fss"]

    print("\n========================================")
    print(f"RFI FREQUENCY: {rfi_mhz} MHz")
    print("========================================")

    print("Without FSS:")
    print(no_file)

    print("With FSS:")
    print(fss_file)

    if not os.path.isfile(no_file):

        print("ERROR: WITHOUT FSS file not found.")
        continue

    if not os.path.isfile(fss_file):

        print("ERROR: WITH FSS file not found.")
        continue

    freq_no, power_no = read_spectrum(
        no_file
    )

    freq_fss, power_fss = read_spectrum(
        fss_file
    )

    # ========================================================
    # INTERPOLATE WITH-FSS ONTO NO-FSS FREQUENCY GRID
    # ========================================================

    power_fss_interp = np.interp(
        freq_no,
        freq_fss,
        power_fss
    )

    # ========================================================
    # FSS ATTENUATION
    # Positive = attenuation
    # A = WITHOUT FSS - WITH FSS
    # ========================================================

    attenuation = (
        power_no -
        power_fss_interp
    )

    # ========================================================
    # LIMIT TO 1–2 GHz
    # ========================================================

    mask = (
        (freq_no >= START_GHZ) &
        (freq_no <= STOP_GHZ)
    )

    freq_plot = freq_no[mask]
    no_plot = power_no[mask]
    fss_plot = power_fss_interp[mask]
    attenuation_plot = attenuation[mask]

    # ========================================================
    # EXACT RFI POWER
    # ========================================================

    rfi_ghz = rfi_mhz / 1000.0

    rfi_no = np.interp(
        rfi_ghz,
        freq_no,
        power_no
    )

    rfi_fss = np.interp(
        rfi_ghz,
        freq_fss,
        power_fss
    )

    rfi_attenuation = (
        rfi_no -
        rfi_fss
    )

    # ========================================================
    # EXACT 1420.4 MHz POWER
    # ========================================================

    h1_ghz = H1_FREQ_MHZ / 1000.0

    h1_no = np.interp(
        h1_ghz,
        freq_no,
        power_no
    )

    h1_fss = np.interp(
        h1_ghz,
        freq_fss,
        power_fss
    )

    h1_attenuation = (
        h1_no -
        h1_fss
    )

    # ========================================================
    # PRINT NUMBERS
    # ========================================================

    print("\nRFI RESULT")
    print(f"RFI frequency       : {rfi_mhz:.1f} MHz")
    print(f"Without FSS         : {rfi_no:.2f} dBm")
    print(f"With FSS            : {rfi_fss:.2f} dBm")
    print(f"RFI attenuation     : {rfi_attenuation:.2f} dB")

    print("\nH1 RESULT")
    print(f"H1 frequency        : {H1_FREQ_MHZ:.1f} MHz")
    print(f"Without FSS         : {h1_no:.2f} dBm")
    print(f"With FSS            : {h1_fss:.2f} dBm")
    print(f"H1 attenuation      : {h1_attenuation:.2f} dB")

    # ========================================================
    # PLOT 1 — WITH vs WITHOUT FSS, 1–2 GHz ONLY
    # ========================================================

    plt.figure(figsize=(11, 6))

    plt.plot(
        freq_plot,
        no_plot,
        label="Without FSS"
    )

    plt.plot(
        freq_plot,
        fss_plot,
        label="With FSS"
    )

    plt.axvline(
        h1_ghz,
        linestyle=":",
        label="H1 = 1420.4 MHz"
    )

    if START_GHZ <= rfi_ghz <= STOP_GHZ:

        plt.axvline(
            rfi_ghz,
            linestyle="--",
            label=f"RFI = {rfi_mhz} MHz"
        )

    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Received Power (dBm)")

    plt.title(
        f"With and Without FSS — "
        f"RFI = {rfi_mhz} MHz"
    )

    plt.xlim(
        START_GHZ,
        STOP_GHZ
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plot1_file = os.path.join(
        OUTPUT_FOLDER,
        f"{rfi_mhz}MHz_With_Without_FSS_1to2GHz.png"
    )

    plt.savefig(
        plot1_file,
        dpi=300,
        bbox_inches="tight"
    )

    print(
        f"Saved plot 1: {plot1_file}"
    )

    plt.show()
    plt.close()

    # ========================================================
    # PLOT 2 — FSS ATTENUATION, 1–2 GHz ONLY
    # ========================================================

    plt.figure(figsize=(11, 6))

    plt.plot(
        freq_plot,
        attenuation_plot,
        label="FSS attenuation"
    )

    plt.axhline(
        0,
        linestyle="--"
    )

    if START_GHZ <= rfi_ghz <= STOP_GHZ:

        plt.scatter(
            rfi_ghz,
            rfi_attenuation,
            s=70,
            zorder=5,
            label=(
                f"RFI {rfi_mhz} MHz: "
                f"{rfi_attenuation:.2f} dB"
            )
        )

        plt.axvline(
            rfi_ghz,
            linestyle="--"
        )

    plt.scatter(
        h1_ghz,
        h1_attenuation,
        s=70,
        zorder=5,
        label=(
            f"H1 1420.4 MHz: "
            f"{h1_attenuation:.2f} dB"
        )
    )

    plt.axvline(
        h1_ghz,
        linestyle=":"
    )

    plt.xlabel("Frequency (GHz)")
    plt.ylabel("FSS Attenuation (dB)")

    plt.title(
        f"FSS Attenuation — "
        f"RFI = {rfi_mhz} MHz"
    )

    plt.xlim(
        START_GHZ,
        STOP_GHZ
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plot2_file = os.path.join(
        OUTPUT_FOLDER,
        f"{rfi_mhz}MHz_FSS_Attenuation_1to2GHz.png"
    )

    plt.savefig(
        plot2_file,
        dpi=300,
        bbox_inches="tight"
    )

    print(
        f"Saved plot 2: {plot2_file}"
    )

    plt.show()
    plt.close()

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    results.append({

        "RFI_MHz":
            rfi_mhz,

        "RFI_No_FSS_dBm":
            rfi_no,

        "RFI_With_FSS_dBm":
            rfi_fss,

        "RFI_Attenuation_dB":
            rfi_attenuation,

        "H1_1420.4_No_FSS_dBm":
            h1_no,

        "H1_1420.4_With_FSS_dBm":
            h1_fss,

        "H1_1420.4_Attenuation_dB":
            h1_attenuation
    })

# ============================================================
# FINAL SUMMARY
# ============================================================

results_df = pd.DataFrame(results)

print("\n\n========================================")
print("FINAL SUMMARY")
print("========================================")

print(
    results_df.round(2).to_string(
        index=False
    )
)

# ============================================================
# SAVE SUMMARY
# ============================================================

summary_file = os.path.join(
    OUTPUT_FOLDER,
    "FSS_analysis_summary.csv"
)

results_df.to_csv(
    summary_file,
    index=False
)

print("\nSaved summary:")
print(os.path.abspath(summary_file))

print("\nAnalysis complete.")

import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ============================================================
# N9342C SETTINGS
# ============================================================

N9342C_IP = "192.168.0.112"

START_FREQ = 500e6
STOP_FREQ  = 2.5e9

RBW = 100e3
VBW = 100e3

# Number of sweeps for averaging
NUM_SWEEPS = 5

rm = pyvisa.ResourceManager("@py")

sa = rm.open_resource(
    f"TCPIP0::{N9342C_IP}::inst0::INSTR"
)

sa.timeout = 60000

# ============================================================
# CHECK INSTRUMENT
# ============================================================

print(sa.query("*IDN?"))

# ============================================================
# CONFIGURE SPECTRUM ANALYZER
# ============================================================

sa.write("INST:SEL SA")

sa.write(f"SENS:FREQ:STAR {START_FREQ}")
sa.write(f"SENS:FREQ:STOP {STOP_FREQ}")

# Spectral resolution < 1 MHz
sa.write(f"SENS:BAND {RBW}")
sa.write(f"SENS:BAND:VID {VBW}")

# Single-sweep mode
sa.write("INIT:CONT 0")

# ASCII trace output
sa.write("FORM:TRAC:DATA ASC")

print("N9342C configured.")
print("Frequency: 500 MHz - 2.5 GHz")
print("RBW: 100 kHz")
print("VBW: 100 kHz")
print(f"Sweeps per measurement: {NUM_SWEEPS}")
print("Individual sweep settings unchanged.")

# ============================================================
# ACQUIRE + AVERAGE MULTIPLE SWEEPS
# ============================================================

def acquire_spectrum(label):

    print(f"\nStarting {NUM_SWEEPS} sweeps for {label}...")

    all_traces = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for sweep_number in range(1, NUM_SWEEPS + 1):

        print(
            f"  Sweep {sweep_number}/{NUM_SWEEPS}..."
        )

        # Start one complete sweep
        sa.write("INIT:IMM")

        # Wait until sweep is finished
        sa.query("*OPC?")

        # Retrieve trace
        raw = sa.query("TRAC:DATA? TRACE1")

        power_dbm = np.array(
            [float(x) for x in raw.strip().split(",")]
        )

        # Frequency axis
        freq_hz = np.linspace(
            START_FREQ,
            STOP_FREQ,
            len(power_dbm)
        )

        all_traces.append(power_dbm)

        # ----------------------------------------------------
        # SAVE INDIVIDUAL SWEEP
        # ----------------------------------------------------

        sweep_filename = (
            f"raw_{label}_"
            f"sweep{sweep_number}_"
            f"{timestamp}.csv"
        )

        np.savetxt(
            sweep_filename,
            np.column_stack(
                (
                    freq_hz / 1e9,
                    power_dbm
                )
            ),
            delimiter=",",
            header="Frequency_GHz,Power_dBm",
            comments=""
        )

        print(
            f"    Saved: {sweep_filename}"
        )

    # ========================================================
    # AVERAGE THE 5 SWEEPS
    # ========================================================

    all_traces = np.array(all_traces)

    # Convert dBm → linear mW
    power_mw = 10 ** (all_traces / 10.0)

    # Average in linear power
    average_power_mw = np.mean(
        power_mw,
        axis=0
    )

    # Convert averaged power back to dBm
    average_power_dbm = (
        10 * np.log10(average_power_mw)
    )

    # ========================================================
    # SAVE AVERAGED SPECTRUM
    # ========================================================

    averaged_filename = (
        f"raw_{label}_"
        f"AVERAGED_{timestamp}.csv"
    )

    np.savetxt(
        averaged_filename,
        np.column_stack(
            (
                freq_hz / 1e9,
                average_power_dbm
            )
        ),
        delimiter=",",
        header="Frequency_GHz,Average_Power_dBm",
        comments=""
    )

    print(
        f"\nAveraged spectrum saved:"
    )
    print(
        f"{averaged_filename}"
    )

    print(
        f"{NUM_SWEEPS} sweeps completed and averaged."
    )

    return freq_hz, average_power_dbm

# ============================================================
# MEASUREMENT 1 — WITHOUT FSS
# ============================================================

input(
    "\nSet up the horns WITHOUT the FSS.\n"
    "Press ENTER to start the 5-sweep measurement..."
)

freq_hz, power_no_fss = acquire_spectrum(
    "NO_FSS"
)

# ============================================================
# MEASUREMENT 2 — WITH FSS
# ============================================================

input(
    "\nInsert the FSS between the horns.\n"
    "Keep everything else unchanged.\n"
    "Press ENTER to start the 5-sweep measurement..."
)

freq_hz, power_fss = acquire_spectrum(
    "WITH_FSS"
)

# ============================================================
# PLOT AVERAGED CURVES
# ============================================================

plt.figure(figsize=(11, 6))

plt.plot(
    freq_hz / 1e9,
    power_no_fss,
    label="Without FSS"
)

plt.plot(
    freq_hz / 1e9,
    power_fss,
    label="With FSS"
)

plt.xlabel("Frequency (GHz)")
plt.ylabel("Received Power (dBm)")

plt.title(
    f"N9342C Raw Spectrum "
    f"({NUM_SWEEPS}-Sweep Average)"
)

plt.grid(True)
plt.legend()
plt.tight_layout()

# Save plot with timestamp
plot_timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

plot_filename = (
    f"FSS_raw_comparison_{plot_timestamp}.png"
)

plt.savefig(
    plot_filename,
    dpi=200
)

print(f"\nPlot saved: {plot_filename}")

plt.show()

# ============================================================
# CLOSE
# ============================================================

sa.close()
rm.close()

print("\nMeasurement finished.")

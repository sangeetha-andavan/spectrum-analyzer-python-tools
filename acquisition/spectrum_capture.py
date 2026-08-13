"""Generic spectrum-analyzer acquisition example.

Uses PyVISA over TCP/IP and common SCPI-style commands. SCPI syntax varies
between instrument models; verify commands against the analyzer manual.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyvisa

ANALYZER_IP = "192.168.1.20"  # Replace with the actual analyzer IP
RESOURCE = f"TCPIP0::{ANALYZER_IP}::INSTR"

START_FREQ = 1.0e9
STOP_FREQ = 2.0e9
RBW = 100e3
VBW = 100e3
POINTS = 1001
SWEEP_TIME = None       # None = automatic
AVERAGING = True
AVERAGES = 5

OUTPUT_DIR = Path("data")


def configure_analyzer(inst):
    inst.write("*CLS")
    inst.write(f"SENS:FREQ:STAR {START_FREQ}")
    inst.write(f"SENS:FREQ:STOP {STOP_FREQ}")
    inst.write(f"SENS:BAND:RES {RBW}")
    inst.write(f"SENS:BAND:VID {VBW}")
    inst.write(f"SWE:POIN {POINTS}")

    if SWEEP_TIME is not None:
        inst.write(f"SWE:TIME {SWEEP_TIME}")

    if AVERAGING:
        inst.write("AVER:STAT ON")
        inst.write(f"AVER:COUN {AVERAGES}")
    else:
        inst.write("AVER:STAT OFF")

    inst.write("FORM:DATA ASC")


def acquire_trace(inst):
    """Acquire one complete trace and return frequency/power arrays."""
    inst.write("INIT:IMM")
    inst.query("*OPC?")

    power = np.asarray(
        inst.query_ascii_values("TRAC:DATA? TRACE1"),
        dtype=float,
    )

    frequency = np.linspace(
        START_FREQ,
        STOP_FREQ,
        len(power),
    )

    return frequency, power


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rm = pyvisa.ResourceManager("@py")
    print("VISA resources:", rm.list_resources())
    print("Connecting:", RESOURCE)

    inst = rm.open_resource(RESOURCE)
    inst.timeout = 60000
    inst.write_termination = "\n"
    inst.read_termination = "\n"

    try:
        print("Instrument:", inst.query("*IDN?").strip())
        configure_analyzer(inst)
        frequency, power = acquire_trace(inst)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"spectrum_{stamp}.csv"

        pd.DataFrame(
            {
                "frequency_hz": frequency,
                "power_dbm": power,
            }
        ).to_csv(output_file, index=False)

        print(f"Saved: {output_file}")

    finally:
        inst.close()
        rm.close()


if __name__ == "__main__":
    main()

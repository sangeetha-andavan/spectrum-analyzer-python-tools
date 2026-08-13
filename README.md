# Spectrum Analyzer Python Tools

Python tools for controlling a spectrum analyzer, acquiring RF spectra, saving measurements, and performing repeatable post-processing.

This repository is intentionally written as a general RF instrumentation project. It does not depend on one particular test article or experiment.

## Measurement workflow

```text
PC
 │
 │ Ethernet / LAN
 ▼
Spectrum Analyzer
 │
 │ RF input
 ▼
Antenna / RF source / test setup

Python → PyVISA → SCPI → Spectrum Analyzer → Trace → CSV → Analysis → Plots
```

## What this project demonstrates

The repository covers the complete measurement chain:

1. Connect a PC to a spectrum analyzer through Ethernet/VISA.
2. Identify the instrument using `*IDN?`.
3. Configure frequency span, RBW, VBW, detector, sweep and averaging.
4. Trigger and acquire a spectrum trace.
5. Transfer frequency/power data to Python.
6. Save the acquired trace as CSV.
7. Analyse and plot the saved data without reconnecting to the instrument.

## Physical connection

For Ethernet control, connect the spectrum analyzer and PC either directly with an Ethernet cable or through the same laboratory LAN.

The analyzer must have a reachable IPv4 address. The PC and analyzer must normally be on compatible IP subnets when using a direct or local-network connection.

Example:

```text
PC Ethernet:       192.168.1.10
Spectrum analyzer: 192.168.1.20
Subnet mask:       255.255.255.0
```

These addresses are examples only. Replace them with the actual addresses configured on the laboratory network.

Before running Python, verify basic network connectivity from the PC:

```text
ping <ANALYZER_IP>
```

Then use the analyzer IP in the VISA resource string. A common VISA TCP/IP instrument resource is:

```text
TCPIP0::<ANALYZER_IP>::INSTR
```

Some instruments instead use HiSLIP or a raw TCP socket. The exact VISA resource and port depend on the analyzer model and its programming interface. PyVISA-py supports TCPIP INSTR and TCPIP SOCKET resources. citeturn0search0turn0search2

## Python environment

Recommended baseline for this repository:

```text
Python 3.10 or newer
```

Current PyVISA releases are tested with Python 3.10+, and current PyVISA-py releases target Python 3.10–3.13. citeturn2search0turn1search1

A virtual environment is recommended:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install the packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Main packages

### PyVISA

PyVISA is the Python front end used to communicate with measurement instruments through VISA. It provides the `ResourceManager`, instrument sessions, queries, writes and trace/data transfer functions. PyVISA supports interfaces including TCP/IP, USB, GPIB and serial communication. citeturn2search0turn0search7

### PyVISA-py

PyVISA-py is the pure-Python VISA backend. It can be selected with:

```python
rm = pyvisa.ResourceManager("@py")
```

This is useful when a vendor/IVI VISA library is not being used. PyVISA-py supports TCPIP INSTR and TCPIP SOCKET resources among other interfaces. citeturn0search0turn0search12

### NumPy

Used for numerical operations on frequency and power arrays.

### Pandas

Used for CSV storage and tabular analysis.

### Matplotlib

Used to generate spectrum plots and comparison plots.

## Package compatibility

The repository uses modern Python 3.10+ tooling. The exact installed versions should be recorded when a working measurement environment is established with:

```bash
python --version
pip show pyvisa
pip show pyvisa-py
pip show numpy
pip show pandas
pip show matplotlib
```

The currently documented PyVISA release line is 1.16.x, and the current PyVISA-py release line is 0.8.x. PyVISA-py 0.8.1 requires Python 3.10 or newer according to its PyPI metadata. citeturn2search3turn1search1

For reproducible laboratory work, the repository should pin the versions that were actually used on the measurement PC rather than assuming that the newest versions will always behave identically.

## Why instrument parameters matter

### Start and stop frequency

These define the frequency region measured by the analyzer. A wider span gives broader spectral coverage but normally reduces the amount of frequency resolution available for a fixed number of sweep points.

### RBW — Resolution Bandwidth

RBW is one of the most important spectrum-analyzer settings. It controls the resolution of the frequency-domain measurement.

Smaller RBW:

```text
better separation of nearby/narrow signals
higher frequency resolution
longer sweep time in many measurements
```

Larger RBW:

```text
faster measurement
lower frequency resolution
nearby signals may become less distinguishable
```

RBW should therefore be selected according to the spectral feature being measured, not simply chosen as an arbitrary value.

### VBW — Video Bandwidth

VBW applies additional filtering to the detected trace. A smaller VBW can make the displayed trace smoother and reduce rapid fluctuations, but can increase measurement time.

### Detector

Peak, positive-peak, negative-peak, sample and average detectors can produce different representations of the same RF spectrum. The detector should remain consistent when comparing measurements.

### Sweep time

Sweep time determines how long the analyzer takes to acquire the selected frequency span. Automatic sweep time is often useful initially because the analyzer can choose a value compatible with the selected RBW and other settings.

### Number of averages

Averaging repeated sweeps can reduce random fluctuations and provide a more stable estimate of the measured spectrum. Averaging is particularly useful when the quantity of interest is small compared with instantaneous noise variations.

## Why use Python instead of manual analyzer operation?

Python automation provides:

```text
repeatability
consistent instrument configuration
automatic sweep acquisition
automatic file naming
automatic CSV storage
batch measurements
reproducible analysis
reduced manual configuration errors
```

The important advantage is not simply convenience. The same measurement state can be reproduced later, which is essential when comparing measurements taken at different times.

## VISA and SCPI relationship

The communication layers can be viewed as:

```text
Python application
       ↓
     PyVISA
       ↓
 VISA backend
       ↓
 Ethernet / USB / GPIB / Serial
       ↓
 Spectrum analyzer
       ↓
       SCPI
```

SCPI commands configure the analyzer and request measurement data. The exact SCPI syntax for frequency, RBW, trace data format, sweep initiation and averaging varies between manufacturers and analyzer families. The acquisition script therefore keeps instrument-specific commands clearly separated and should always be checked against the analyzer programming manual.

## Typical connection test

After installing the packages, run the basic VISA discovery test:

```python
import pyvisa

rm = pyvisa.ResourceManager("@py")
print(rm.list_resources())
```

For a known TCP/IP address:

```python
import pyvisa

ANALYZER_IP = "192.168.1.20"   # replace with the actual analyzer IP
RESOURCE = f"TCPIP0::{ANALYZER_IP}::INSTR"

rm = pyvisa.ResourceManager("@py")
instrument = rm.open_resource(RESOURCE)
print(instrument.query("*IDN?"))
instrument.close()
rm.close()
```

PyVISA documentation uses `ResourceManager` and `open_resource()` for instrument sessions, including TCP/IP resources. citeturn0search7turn0search2

## Acquisition and analysis separation

The project deliberately separates measurement from analysis.

```text
acquisition/
    spectrum_capture.py

        ↓ CSV

data/

        ↓

analysis/
    spectrum_analysis.py

        ↓

plots/
```

This allows the analyzer to be used only when collecting data. The analysis script can then be run repeatedly on the saved CSV files without occupying or reconnecting to the instrument.

## Repository structure

```text
spectrum-analyzer-python-tools/
├── acquisition/
│   └── spectrum_capture.py
├── analysis/
│   └── spectrum_analysis.py
├── data/
├── plots/
├── requirements.txt
└── README.md
```

## Instrument-specific adaptation

Before connecting to a real analyzer, verify:

```text
instrument model
firmware/version
VISA interface/resource name
SCPI programming manual
TCP/IP control method and port, if applicable
trace data format
frequency-axis query
power-axis query
sweep completion method
```

Do not assume that SCPI commands from one analyzer manufacturer will work unchanged on another model.

## Scope

This repository is a reusable example of automated RF spectrum acquisition and analysis. It is not tied to a particular test article, antenna, filter, or experimental result.

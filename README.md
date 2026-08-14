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

Some instruments instead use HiSLIP or a raw TCP socket. The exact VISA resource and port depend on the analyzer model and its programming interface.

## Python environment

Recommended baseline for this repository:

```text
Python 3.10 or newer
```

Create a virtual environment:

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

PyVISA is the Python interface used to communicate with measurement instruments through VISA. It provides instrument sessions, queries, writes, and data-transfer functions.

### PyVISA-py

PyVISA-py is a pure-Python VISA backend. The scripts in this repository use:

```python
rm = pyvisa.ResourceManager("@py")
```

This allows instrument communication without relying on a separate vendor VISA implementation when the supported interface is available.

### NumPy

Used for numerical operations on frequency and power arrays.

### Pandas

Used for CSV storage and analysis.

### Matplotlib

Used to generate spectrum and comparison plots.

## Package compatibility

The repository uses Python 3.10+ as the recommended baseline. Record the exact environment used for a laboratory measurement with:

```bash
python --version
pip show pyvisa
pip show pyvisa-py
pip show numpy
pip show pandas
pip show matplotlib
```

For reproducible measurements, pin the package versions actually validated on the measurement PC rather than assuming that future releases will behave identically.

## Why analyzer parameters matter

### Start and stop frequency

These define the measured frequency region. A wider span provides broader coverage but can reduce the amount of detail available for a fixed number of sweep points.

### RBW — Resolution Bandwidth

RBW is the frequency-domain resolution of the measurement. It is especially important when the signals of interest are narrowband.

A smaller RBW allows the analyzer to distinguish narrower spectral features and generally includes less noise power in each resolution bandwidth. The trade-off is a longer sweep time.

A larger RBW reduces the measurement time but can make narrow spectral features less distinguishable and increases the noise power measured within each resolution bandwidth.

### VBW — Video Bandwidth

VBW applies additional filtering to the detected trace. A smaller VBW can smooth rapid fluctuations in the displayed trace, but may increase measurement time.

### Sweep time

Sweep time controls how long the analyzer takes to scan the selected span. It is affected by settings such as RBW and VBW.

### Number of averages

Averaging repeated sweeps can reduce random fluctuations and produce a more stable estimate of the spectrum.

## Practical RBW example: signal visibility

A simple measurement was made with the same physical setup while changing the RBW. The center frequency and span were kept at 1.5 GHz and 2 GHz respectively. VBW was kept equal to RBW.

### Measured settings

| Parameter | 100 kHz RBW | 3 MHz RBW |
|---|---:|---:|
| RBW | 100 kHz | 3 MHz |
| VBW | 100 kHz | 3 MHz |
| Center frequency | 1.5 GHz | 1.5 GHz |
| Span | 2 GHz | 2 GHz |
| Sweep time | 3.874 s | 90.56 ms |

### What changes visually?

With 100 kHz RBW, the narrow H1 and RF-source spectral features are much easier to distinguish from the surrounding noise.

With 3 MHz RBW, the same features become much less distinct and can approach the noise background.

The RBW ratio is:

\[
\frac{3\,\mathrm{MHz}}{100\,\mathrm{kHz}}=30
\]

For approximately white noise, the corresponding increase in integrated noise power is:

\[
10\log_{10}(30)\approx14.8\,\mathrm{dB}
\]

This helps explain why the wider 3 MHz measurement has a higher noise contribution within each resolution bandwidth. The actual RF signals have not simply become weaker; the analyzer is measuring them through a much wider resolution filter.

### Spectral resolution in practice

Spectral resolution is the ability of the analyzer to distinguish spectral components that are close together in frequency. It is not simply a matter of making a graph look sharper.

When the signal is narrow compared with the RBW, a large RBW can merge nearby spectral components and increase the noise contribution. A smaller RBW provides finer frequency discrimination and can make narrow signals visible above the noise floor.

The practical trade-off is therefore:

```text
Smaller RBW  → better spectral resolution → better narrow-signal visibility → slower sweep
Larger RBW   → lower spectral resolution → faster sweep → more noise per RBW
```

## Why use Python instead of manual operation?

Python automation provides consistent instrument configuration, repeatable sweeps, automatic data storage, batch measurements, and reproducible analysis. It also makes repeated averaging practical without manually repeating the same analyzer operations.

The important advantage is repeatability: the same measurement state can be reproduced later instead of relying on a sequence of manual front-panel settings.

## VISA and SCPI relationship

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

SCPI commands configure the analyzer and request measurement data. The exact command syntax varies between analyzer manufacturers and models, so the programming manual for the specific instrument should always be checked.

## Typical connection test

```python
import pyvisa

rm = pyvisa.ResourceManager("@py")
print(rm.list_resources())
```

For a known TCP/IP address:

```python
import pyvisa

ANALYZER_IP = "192.168.1.20"   # replace with your analyzer IP
RESOURCE = f"TCPIP0::{ANALYZER_IP}::INSTR"

rm = pyvisa.ResourceManager("@py")
instrument = rm.open_resource(RESOURCE)
print(instrument.query("*IDN?"))
instrument.close()
rm.close()
```

## Acquisition and analysis separation

The project separates instrument control from post-processing:

```text
acquisition/
    SA_code.py

        ↓ CSV

analysis/
    analysis_3.py

        ↓

plots + numerical results
```

The analyzer is therefore needed when collecting measurements, while the saved CSV data can be analysed repeatedly without reconnecting to the instrument.

## Repository structure

```text
spectrum-analyzer-python-tools/
├── acquisition/
│   └── SA_code.py
├── analysis/
│   └── analysis_3.py
├── images/
│   ├── rbw_100khz.jpg
│   └── rbw_3mhz.jpg
├── data/
├── plots/
├── requirements.txt
└── README.md
```

## Instrument-specific adaptation

Before connecting to a real analyzer, verify the instrument model, firmware, VISA resource, TCP/IP control method, SCPI programming manual, trace format, frequency-axis query, power-axis query, and sweep-completion method.

Do not assume that SCPI commands from one analyzer model will work unchanged on another.

## Scope

This repository is a reusable example of automated RF spectrum acquisition and analysis. It is not tied to a particular test article, antenna, filter, or experimental result.

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

The analyzer must have a reachable IPv4 address. The PC and analyzer should normally be on compatible IP subnets.

Example only:

```text
PC Ethernet:       192.168.1.10
Spectrum analyzer: 192.168.1.20
Subnet mask:       255.255.255.0
```

Replace these example values with the network settings used in your laboratory.

Check connectivity first:

```bash
ping <ANALYZER_IP>
```

A common VISA TCP/IP instrument resource is:

```text
TCPIP0::<ANALYZER_IP>::INSTR
```

The exact resource format depends on the analyzer and VISA interface.

## Python environment

Recommended baseline: **Python 3.10 or newer**.

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it and install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Record the exact environment used for a measurement with:

```bash
python --version
pip show pyvisa
pip show pyvisa-py
pip show numpy
pip show pandas
pip show matplotlib
```

## Main packages

**PyVISA** provides the Python interface to VISA instruments and handles resource sessions, queries, writes, and data transfer.

**PyVISA-py** is a pure-Python VISA backend. The acquisition code selects it with:

```python
rm = pyvisa.ResourceManager("@py")
```

**NumPy** is used for numerical operations on frequency and power arrays.

**Pandas** is used for CSV-based analysis.

**Matplotlib** is used to generate spectrum and comparison plots.

For reproducible laboratory work, pin the exact package versions that have been validated on the measurement PC.

## Why analyzer parameters matter

### Start and stop frequency

These define the measured frequency region. A wider span gives broader coverage, while a smaller span can make a particular spectral region easier to inspect.

### RBW — Resolution Bandwidth

RBW is the analyzer's frequency resolution. It is especially important when the signals of interest are narrowband.

A smaller RBW allows finer frequency discrimination and generally includes less noise power within each resolution bandwidth. The trade-off is a longer sweep time.

A larger RBW allows faster measurements, but nearby or narrow spectral features can become less distinguishable and the noise power measured within each resolution bandwidth increases.

### VBW — Video Bandwidth

VBW applies additional filtering to the detected trace. A smaller VBW can smooth rapid fluctuations, but may increase measurement time.

### Sweep time

Sweep time is the time required to scan the selected frequency span. Settings such as RBW and VBW can strongly affect it.

### Number of averages

Averaging repeated sweeps reduces random fluctuations and produces a more stable estimate of the spectrum.

## RBW in practice: why signal visibility changes

The following two measurements used the same physical setup, center frequency, and span. Only the RBW/VBW settings were changed.

### Measured settings

| Parameter | RBW = 100 kHz | RBW = 3 MHz |
|---|---:|---:|
| Resolution bandwidth | 100 kHz | 3 MHz |
| Video bandwidth | 100 kHz | 3 MHz |
| Center frequency | 1.5 GHz | 1.5 GHz |
| Span | 2 GHz | 2 GHz |
| Sweep time | 3.874 s | 90.56 ms |

### What changes visually?

With **100 kHz RBW**, the narrow H1 and RF-source features are much easier to distinguish from the surrounding noise.

With **3 MHz RBW**, the same features become much less distinct and can approach the noise background.

The RBW change is:

```text
3 MHz / 100 kHz = 30
```

For approximately white noise, the corresponding change in integrated noise power is:

```text
10 × log10(30) ≈ 14.8 dB
```

So the 3 MHz measurement includes substantially more noise power within each resolution bandwidth. The RF signals themselves have not simply become weaker; the analyzer is observing them through a much wider resolution filter.

### Why spectral resolution matters

Spectral resolution is the ability of the analyzer to distinguish spectral components that are close together in frequency.

A narrow signal can be visible at a small RBW because the measurement bandwidth is narrow enough to separate the signal from more of the surrounding noise. At a much larger RBW, nearby components can merge and the increased noise contribution can make a narrow signal harder to distinguish.

The practical trade-off is:

```text
Smaller RBW → finer spectral resolution → better narrow-signal visibility → slower sweep
Larger RBW  → coarser spectral resolution → faster sweep → more noise power per RBW
```

This is why RBW is a measurement parameter, not merely a display setting.

## Why use Python instead of manual operation?

Python automation provides consistent instrument configuration, repeatable sweeps, automatic data storage, batch measurements, and reproducible analysis.

It is particularly useful when several sweeps must be acquired and averaged with identical settings.

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

SCPI commands configure the analyzer and request measurement data. The exact command syntax varies between analyzer manufacturers and models, so the instrument programming manual should always be checked.

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

The analyzer is needed during measurement acquisition. Once the CSV files are saved, the analysis can be repeated without reconnecting to the instrument.

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

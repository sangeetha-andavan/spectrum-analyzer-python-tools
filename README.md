# Spectrum Analyzer Python Tools

Python tools for controlling a spectrum analyzer, acquiring RF spectra, saving measurements, and performing repeatable post-processing.

This is a general RF instrumentation project. It is not tied to one particular test article or experiment.

## 1. Measurement workflow

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

The workflow is:

1. Connect the PC to the spectrum analyzer.
2. Verify network/VISA communication.
3. Configure the frequency range and analyzer settings.
4. Start and complete the sweep.
5. Read the trace into Python.
6. Save the measurement as CSV.
7. Analyse the saved data and generate plots.

## 2. Physical connection and IP configuration

For Ethernet control, connect the PC and spectrum analyzer directly with Ethernet or connect both to the same laboratory LAN.

The analyzer needs a reachable IPv4 address. The PC and analyzer should normally be on compatible subnets.

Example only:

```text
PC                 192.168.1.10
Spectrum analyzer  192.168.1.20
Subnet mask        255.255.255.0
```

Do not copy these example values into a real setup. Replace them with the values used by your laboratory network.

First test the connection from the PC:

```bash
ping <ANALYZER_IP>
```

A common VISA TCP/IP resource is:

```text
TCPIP0::<ANALYZER_IP>::INSTR
```

The exact VISA resource depends on the analyzer and the supported interface.

## 3. Python environment and packages

Recommended baseline: **Python 3.10 or newer**.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Install the packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check the installed environment:

```bash
python --version
pip show pyvisa
pip show pyvisa-py
pip show numpy
pip show pandas
pip show matplotlib
```

### Packages used

**PyVISA** — Python interface for VISA instrument communication.

**PyVISA-py** — pure-Python VISA backend selected in the acquisition script with:

```python
rm = pyvisa.ResourceManager("@py")
```

**NumPy** — numerical operations on frequency and power arrays.

**Pandas** — CSV loading and tabular analysis.

**Matplotlib** — spectrum and comparison plots.

For reproducible measurements, record and pin the package versions that were actually validated on the measurement PC.

## 4. Why analyzer parameters matter

### Start and stop frequency

These define the frequency region being measured.

A wider span gives broader coverage. A narrower span can make a selected spectral region easier to inspect.

### RBW — Resolution Bandwidth

RBW is the analyzer's frequency resolution. It is especially important when the signals of interest are narrowband.

A smaller RBW gives finer frequency discrimination and normally includes less noise power in each resolution bandwidth, but the analyzer generally needs more time to sweep the same span.

A larger RBW allows a faster sweep, but narrow or closely spaced spectral components become less distinguishable and more noise power is included within each resolution bandwidth.

### VBW — Video Bandwidth

VBW applies additional filtering to the detected trace. A smaller VBW can smooth short-term fluctuations, but may increase measurement time.

### Sweep time

Sweep time is the time used to scan the selected frequency span. RBW and VBW are among the settings that can affect it.

### Number of averages

Averaging repeated sweeps reduces random fluctuations and gives a more stable estimate of the spectrum.

## 5. RBW in practice: signal visibility

The following two measurements used the same physical setup, center frequency, and span. The RBW and VBW were changed together.

### Measured settings

| Parameter | 100 kHz RBW | 3 MHz RBW |
|---|---:|---:|
| RBW | 100 kHz | 3 MHz |
| VBW | 100 kHz | 3 MHz |
| Center frequency | 1.5 GHz | 1.5 GHz |
| Span | 2 GHz | 2 GHz |
| Sweep time | 3.874 s | 90.56 ms |

### 100 kHz RBW

With 100 kHz RBW, the narrow H1 and RF-source features are clearly visible above the surrounding noise.

![Spectrum with 100 kHz RBW](images/rbw_100khz.jpg)

### 3 MHz RBW

With 3 MHz RBW, the same narrow features become much less distinct and approach the noise background.

![Spectrum with 3 MHz RBW](images/rbw_3mhz.jpg)

### What causes the visibility change?

The RBW changes by a factor of 30:

```text
3 MHz ÷ 100 kHz = 30
```

For approximately white noise, the change in integrated noise power is:

```text
10 × log10(30) ≈ 14.8 dB
```

This means that a much wider RBW admits substantially more noise power into each resolution bandwidth.

The important point is that the RF signal itself has not simply become weaker. The analyzer is measuring it through a much wider resolution filter, so the signal is less separated from the surrounding noise.

### What is spectral resolution?

Spectral resolution is the ability of the analyzer to distinguish spectral components that are close together in frequency.

It is not simply about making a graph look sharper. A sufficiently small RBW allows narrow signals to be separated from nearby spectral components and from more of the noise background.

### Practical trade-off

```text
Smaller RBW
    ↓
finer spectral resolution
    ↓
better narrow-signal visibility
    ↓
slower sweep
```

```text
Larger RBW
    ↓
coarser spectral resolution
    ↓
faster sweep
    ↓
more noise power per RBW
```

The two measurements demonstrate this trade-off directly: 100 kHz RBW produced a 3.874 s sweep, while 3 MHz RBW produced a 90.56 ms sweep.

RBW is therefore an important measurement setting, not just a display setting.

## 6. Why use Python instead of manual operation?

Python automation provides:

```text
consistent instrument configuration
repeatable sweeps
automatic data storage
batch measurements
repeatable averaging
reproducible analysis
reduced manual configuration errors
```

The main benefit is repeatability. The same measurement state can be reproduced without repeatedly setting every analyzer parameter from the front panel.

## 7. VISA and SCPI relationship

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

SCPI commands configure the analyzer and request measurement data. The exact syntax varies between analyzer manufacturers and models, so the instrument programming manual should always be checked.

## 8. Basic VISA connection test

Start by checking which VISA resources are visible:

```python
import pyvisa

rm = pyvisa.ResourceManager("@py")
print(rm.list_resources())
```

For a known TCP/IP address:

```python
import pyvisa

ANALYZER_IP = "<ANALYZER_IP>"
RESOURCE = f"TCPIP0::{ANALYZER_IP}::INSTR"

rm = pyvisa.ResourceManager("@py")
instrument = rm.open_resource(RESOURCE)

print(instrument.query("*IDN?"))

instrument.close()
rm.close()
```

## 9. Acquisition and analysis separation

The project separates instrument control from post-processing.

```text
acquisition/
    N9342C_spectrum_capture.py

        ↓ CSV

analysis/
    basic_analysis.py

        ↓

plots + numerical results
```

The analyzer is needed during acquisition. Once the CSV files are saved, the analysis can be repeated without reconnecting to the instrument.

## 10. Repository structure

```text
spectrum-analyzer-python-tools/
├── acquisition/
│   └── N9342C_spectrum_capture.py
├── analysis/
│   └── basic_analysis.py
├── images/
│   ├── rbw_100khz.jpg
│   └── rbw_3mhz.jpg
├── requirements.txt
└── README.md
```

## 11. Instrument-specific adaptation

Before connecting to a real analyzer, verify:

```text
instrument model
firmware/version
VISA resource
TCP/IP control method
SCPI programming manual
trace data format
frequency-axis query
power-axis query
sweep-completion method
```

Do not assume that SCPI commands from one analyzer model will work unchanged on another.

## 12. Scope

This repository is a reusable example of automated RF spectrum acquisition and analysis. It is not tied to a particular test article, antenna, filter, or experimental result.

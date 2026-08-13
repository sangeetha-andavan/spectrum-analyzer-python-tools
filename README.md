# Spectrum Analyzer Python Tools

Python tools for controlling a spectrum analyzer, acquiring RF spectra, saving measurements, and performing basic post-processing.

## Purpose

This repository demonstrates a repeatable workflow for RF spectrum measurements using Python and PyVISA.

The workflow is:

```text
Python → PyVISA → Spectrum Analyzer → Spectrum Trace → CSV → Analysis/Plots
```

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

## Why automate the analyzer?

Automation makes repeated measurements consistent and reduces manual configuration errors. The same frequency range, RBW, VBW, detector, sweep settings, and averaging can be applied to every measurement. Traces can also be saved automatically for later analysis.

## Important analyzer parameters

### Frequency range

`START_FREQ` and `STOP_FREQ` define the part of the spectrum being measured.

### RBW — Resolution Bandwidth

RBW determines the frequency resolution of the measurement. A smaller RBW helps resolve narrow or closely spaced signals, while a larger RBW generally gives faster sweeps but less frequency resolution.

### VBW — Video Bandwidth

VBW controls additional video filtering/smoothing of the detected trace. Lower VBW can reduce displayed noise fluctuations but may increase measurement time.

### Sweep time

Sweep time controls how quickly the analyzer scans the selected frequency range. The analyzer may also be allowed to choose an automatic sweep time appropriate for the selected settings.

### Detector and trace mode

Detector and trace settings determine how the analyzer represents the measured signal. These should be kept consistent when comparing repeated measurements.

### Averaging

Averaging multiple sweeps can reduce random measurement fluctuations and produce a more stable spectrum. The number of averages should be selected according to the measurement objective and available acquisition time.

## Why use code instead of manual operation?

Python automation provides repeatability, automatic data storage, batch measurements, consistent instrument configuration, and reproducible analysis.

## Instrument communication

The example acquisition script uses PyVISA and SCPI commands. SCPI command syntax varies between analyzer manufacturers and models, so the instrument-specific commands may need to be adjusted.

## Basic workflow

1. Connect the analyzer through VISA.
2. Reset or configure the measurement state as required.
3. Set frequency range and measurement parameters.
4. Start a sweep and wait for completion.
5. Read the frequency axis and spectrum trace.
6. Save the data as CSV.
7. Use the analysis script to generate plots.

## Requirements

Python 3.9+ and the packages listed in `requirements.txt`.

A VISA implementation such as NI-VISA or another compatible VISA backend is also required for instrument communication.

## Notes

This repository is intentionally instrument-agnostic. Always verify the SCPI programming manual for the specific spectrum analyzer being used.

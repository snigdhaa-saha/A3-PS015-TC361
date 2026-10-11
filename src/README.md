# NetSages — Network Connectivity Diagnostics

## Overview

NetSages is a network diagnostics project that measures connectivity-related indicators and presents the results in a structured report.

## Current Implementation

The `measurements` package contains:

- **Latency measurement:** Measures ping response times and packet loss.
- **DNS measurement:** Checks hostname resolution and records lookup time.
- **Connectivity measurement:** Checks whether a TCP connection can be established with a specified host and port.
- **Measurement runner:** Executes the measurements and prints a combined JSON report.

## Project Structure

```text
src/
├── README.md
├── measurements/
│   ├── __init__.py
│   ├── latency.py
│   ├── dns.py
│   ├── connectivity.py
│   └── run_measurements.py
└── tests/
    ├── test_latency.py
    ├── test_dns.py
    └── test_connectivity.py
```

## Requirements

- Python 3
- Network access for live measurements
- A system with the `ping` command available for latency measurement

## Run the Measurements

Open a terminal in the `src` directory and run:

```bash
python3 -m measurements.run_measurements
```

The program prints a JSON report containing a UTC timestamp and the latency, DNS, and TCP connectivity results.

## Run the Tests

From the `src` directory, run:

```bash
python3 -m unittest discover -s tests -v
```

The tests use mocked network operations where appropriate, so they can verify expected behavior without relying on live network responses.

## Scope of This Implementation

This version implements the initial measurement layer. It does not yet represent a complete diagnosis or explanation engine.

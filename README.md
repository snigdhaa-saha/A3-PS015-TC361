NetSages — AIORI-3 Hackathon Project
NetSages is a network connectivity diagnostics project developed for the AIORI-3 Hackathon.

Project Overview
The project aims to measure network performance, identify connectivity-related issues, and work toward providing understandable, evidence-based diagnoses for home and last-mile internet connectivity.
Current Implementation:
The initial implementation provides:
- Latency measurement: Ping response times and packet-loss statistics.
- DNS resolution: Hostname resolution status and lookup duration.
- TCP connectivity: Reachability checks for a specified host and port.
- Structured reporting: A combined JSON report containing measurement results.

Repository Structure:
- `src/measurements/` — Network measurement modules and execution runner.
- `src/tests/` — Automated unit tests.
- `src/README.md` — Implementation details and instructions for running the code.
- `Proposed-structure-hackathon.pdf` — Proposed project structure document.

Running the Implementation:
From the `src` directory, run:

```bash
python -m measurements.run_measurements
```

To run the unit tests:

```bash
python -m unittest discover -s tests -v
```

Development Status:
The repository currently contains the initial network measurement layer. Diagnosis, explainability, and further project components will be developed and integrated as the project progresses.

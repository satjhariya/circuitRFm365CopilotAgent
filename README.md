# CircuitRF Microsoft 365 Copilot Agent

### Expert Aerospace & Defence RF Component Design & Architecture Copilot Extension

This repository contains the complete implementation, packaging, and local execution bridge for a custom **Microsoft 365 Copilot Agent** designed for Expert RF Engineers working in aerospace, defence, radar, electronic warfare (EW), and SATCOM applications.

The agent enables Microsoft 365 Copilot to:
1. **Deconstruct RF Requirements**: Break down high-level system requirements into incremental engineering steps and stage-by-stage budgets.
2. **Drive CircuitRF Simulations**: Directly synthesize `.cnl` netlists and execute S-parameter sweeps via CircuitRF CLI and MCP interfaces.
3. **Analyze Cascaded Lineups**: Compute Friis Noise Figure, overall Gain, cumulative $OIP3/IIP3$, $P_{1dB}$, and DC power consumption.
4. **Compile Professional Word Reports**: Generate defence-grade Technical Memorandums (`.docx`) with embedded S-parameter plots and compliance tables (with LibreOffice CLI PDF export).
5. **Export Multi-Tab Excel Workbooks**: Produce structured spreadsheets (`.xlsx`) with conditional formatting for compliance matrices, cascaded lineup budgets, and Touchstone data tables.

---

## Quick Start

### 1. Package the M365 Copilot Agent
```bash
python scripts/package_agent.py
```
This generates `circuitrf-copilot-agent.zip`, ready for sideloading into Microsoft Teams Developer Portal, Copilot Studio, or M365 Admin Center.

### 2. Launch the Workstation Bridge Server
- **On Windows Work PC**:
  ```cmd
  scripts\start_bridge.bat
  ```
- **On Linux / WSL**:
  ```bash
  scripts/start_bridge.sh
  ```
Access the interactive Swagger UI at: `http://127.0.0.1:8000/docs`

### 3. Run the End-to-End Test Suite
```bash
python scripts/test_workflow.py
```
This verifies:
- Cascaded Friis Noise Figure calculation.
- CircuitRF netlist generation and S-parameter simulation.
- Aerospace compliance evaluation (MIL-PRF-38534 & DO-160G).
- Word document generation (`.docx`) and LibreOffice PDF conversion.
- Excel workbook generation (`.xlsx`).

---

## Project Structure

```
/home/satish/Documents/Code/dev/agent/
├── appPackage/                      # M365 Copilot Declarative Agent Package
│   ├── manifest.json                # Teams App Manifest v1.17
│   ├── declarativeAgent.json        # Agent instructions, persona & actions
│   ├── ai-plugin.json               # AI Plugin definition
│   ├── openapi.yaml                 # REST API specification for Copilot
│   ├── color.png                    # 192x192 Agent icon
│   └── outline.png                  # 32x32 Agent outline icon
├── bridge_server/                   # Local Workstation Bridge Server
│   ├── server.py                    # FastAPI REST endpoints
│   ├── circuitrf_client.py          # CircuitRF MCP client & CLI runner
│   ├── report_generator.py          # Word (.docx) & LibreOffice CLI PDF engine
│   └── excel_generator.py           # Multi-tab Excel (.xlsx) workbook engine
├── rf_engine/                       # RF Engineering & Defence Algorithms
│   ├── cascade.py                   # Friis Noise Figure & IP3 cascade equations
│   ├── matching.py                  # L-match, Pi/T pads, and impedance math
│   ├── military_specs.py            # DO-160G, MIL-STD-883, and de-rating margins
│   └── netlist_builder.py           # CircuitRF .cnl netlist builder
├── scripts/                         # Automation & Launcher Scripts
│   ├── start_bridge.bat             # Windows launcher
│   ├── start_bridge.sh              # Linux launcher
│   ├── package_agent.py             # Packaging script
│   └── test_workflow.py             # Verification script
├── samples/                         # Benchmark Requirements & Demos
│   ├── sample_requirements.json     # Pre-configured radar/SATCOM benchmarks
│   └── sample_run.py                # Standalone demo run
├── docs/                            # Comprehensive Documentation
│   ├── DEPLOYMENT_GUIDE.md          # Sideloading & Windows setup instructions
│   ├── USER_MANUAL.md               # Prompting guide and scenario workflows
│   └── ARCHITECTURE.md              # System architecture & data boundaries
├── requirements.txt                 # Python dependencies
└── circuitrf-copilot-agent.zip      # Deployable M365 Copilot Package
```

---

## Detailed Documentation
- [Deployment Guide](file:///home/satish/Documents/Code/dev/agent/docs/DEPLOYMENT_GUIDE.md)
- [User Manual](file:///home/satish/Documents/Code/dev/agent/docs/USER_MANUAL.md)
- [Architecture & Security](file:///home/satish/Documents/Code/dev/agent/docs/ARCHITECTURE.md)

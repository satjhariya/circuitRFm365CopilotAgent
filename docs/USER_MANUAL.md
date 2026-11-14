# CircuitRF M365 Copilot Agent: RF Engineer User Manual

This manual provides instructions and prompt templates for RF systems and component engineers utilizing the **CircuitRF Aerospace & Defence Engineering Copilot Agent** in Microsoft 365 Copilot.

---

## 1. Agent Persona & Capabilities

The agent acts as a **Senior Principal Aerospace & Defence RF Systems Architect** with comprehensive capabilities:
- **RF Requirement Decomposition**: Converts mission-level constraints (frequency bands, jamming margins, noise figure, link budget) into incremental block-level specifications.
- **CircuitRF Automation**: Generates syntax-verified `.cnl` netlists, triggers S-parameter sweeps, evaluates return loss and insertion loss, and processes Touchstone (`.s2p`) files.
- **Cascaded Lineup Analysis**: Solves Friis Noise Figure equations, cascaded Output/Input Third-Order Intercept Points ($OIP3 / IIP3$), and 1 dB compression ($P_{1dB}$).
- **Aerospace Compliance**: Checks military de-rating rules (50% power/voltage), temperature ranges ($-55^\circ\text{C}$ to $+125^\circ\text{C}$), and RTCA DO-160G / MIL-PRF-38534 standards.
- **Automated Office Deliverables**: Produces complete Word Technical Memorandums (`.docx`) with embedded S-parameter plots and multi-tab Excel (`.xlsx`) data books.

---

## 2. Typical Prompt Scenarios

### Scenario 1: High-Level System Requirement Ingestion
**User Prompt:**
> *"I need an X-band airborne radar front-end receiver operating at 10 GHz with a 1 GHz bandwidth. Overall gain must be at least 24 dB, noise figure under 2.2 dB, and OIP3 greater than 32 dBm. Deconstruct this requirement into incremental steps and propose a stage-by-stage lineup."*

**Agent Action:**
- Calls `/api/rf/decompose`.
- Analyzes MIL-STD-883 and DO-160 temperature requirements.
- Breaks the system into 5 incremental execution steps.
- Proposes a lineup: Pre-selector BPF, Low-Noise GaN MMIC, Interstage Attenuator Pad, and High-Linearity Driver Amplifier.

---

### Scenario 2: CircuitRF Component Synthesis & Simulation
**User Prompt:**
> *"Synthesize the pre-selector bandpass filter for the 10 GHz radar front-end in CircuitRF and run an S-parameter sweep from 8 to 12 GHz. Check return loss and 3 dB bandwidth."*

**Agent Action:**
- Calls `/api/rf/synthesize_netlist` with `circuit_type="bandpass_filter"`, `f0_ghz=10.0`, `bw_ghz=1.0`.
- Generates `XBand_Preselector.cnl` with input/output 50 $\Omega$ ports and coupled LC resonator stages.
- Calls `/api/rf/simulate`.
- Extracts $S_{11}$ return loss minimum and $S_{21}$ passband transmission.

---

### Scenario 3: Cascaded Friis Lineup & Linearity Calculation
**User Prompt:**
> *"Calculate the cascaded noise figure, overall gain, and OIP3 for this receiver chain:*
> *- Stage 1: Filter (-1.2 dB gain, 1.2 dB NF)*
> *- Stage 2: LNA (+16.5 dB gain, 1.1 dB NF, +30 dBm OIP3)*
> *- Stage 3: Pad (-3.0 dB gain, 3.0 dB NF)*
> *- Stage 4: Driver (+14.0 dB gain, 2.8 dB NF, +36 dBm OIP3)*
> *Compare the result against our target specs."*

**Agent Action:**
- Calls `/api/rf/cascade`.
- Applies the Friis formula to compute:
  $$F_{total} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2} + \frac{F_4 - 1}{G_1 G_2 G_3}$$
- Computes cascaded $OIP3$ and generates a compliance matrix with Pass/Marginal/Fail status.

---

### Scenario 4: Compiling Deliverables in Word & Excel
**User Prompt:**
> *"Compile these simulation results, the cascaded lineup, and the compliance matrix into a Word engineering memorandum (.docx) and export the data points to an Excel spreadsheet (.xlsx)."*

**Agent Action:**
- Calls `/api/report/docx`:
  - Builds a formal technical memorandum formatted for aerospace defence contractors.
  - Embeds high-resolution Matplotlib S-parameter frequency response plots ($S_{11}$ and $S_{21}$).
  - Formats tables with executive summary, metadata, and engineering sign-off fields.
  - Generates PDF via LibreOffice CLI (`soffice --headless --convert-to pdf`).
- Calls `/api/report/xlsx`:
  - Tab 1: Compliance Matrix with green/yellow/red conditional status formatting.
  - Tab 2: Cascaded Lineup Budget with stage-by-stage cumulative values.
  - Tab 3: CircuitRF S-Parameters Dataset with frequency, $S_{11}, S_{21}, S_{12}, S_{22}$, and VSWR.
- Returns the local paths to the generated files.

---

## 3. Engineering Guidelines & Tips
- **Physical Units**: The agent expects standard engineering units ($GHz, MHz, dB, dBm, nH, pF, \Omega$).
- **De-rating Rules**: By default, the agent enforces a 50% electrical power de-rating on resistive components and 60% voltage de-rating on capacitors in accordance with aerospace mission profiles.
- **Offline Reliability**: The agent features an integrated high-precision numerical RF solver that operates seamlessly even when the CircuitRF daemon is offline or handling external locks.

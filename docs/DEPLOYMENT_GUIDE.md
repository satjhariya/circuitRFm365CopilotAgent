# Microsoft 365 Copilot CircuitRF Agent Deployment Guide

This guide details how to configure, package, and deploy the **CircuitRF Aerospace & Defence Engineering Copilot Agent** onto a Windows Work PC with base Microsoft 365 Copilot.

---

## 1. System Prerequisites

1. **Host Workstation (Windows 10/11 Work PC)**:
   - Microsoft 365 Enterprise account with Copilot license enabled.
   - CircuitRF installed and accessible (via CLI `circuitrf` or MCP daemon).
   - Python 3.10+ installed and added to system `PATH`.
   - Microsoft Word and Excel (or LibreOffice with `soffice` in PATH for headless conversion).
2. **Connectivity & Sideloading Tooling**:
   - Permission to sideload custom apps in Microsoft Teams / M365 (via **Teams Developer Portal** or **Microsoft 365 Admin Center**).
   - Dev Tunnels CLI (`devtunnel`) or Ngrok to expose the local Bridge API securely to Microsoft Cloud.

---

## 2. Directory Layout

The agent solution is located at:
```
/home/satish/Documents/Code/dev/agent/  (or C:\Users\<Username>\Documents\Code\dev\agent on Windows)
├── appPackage/
│   ├── manifest.json              # M365 App Manifest v1.17
│   ├── declarativeAgent.json      # Declarative Agent instructions & actions
│   ├── ai-plugin.json             # AI Plugin definition
│   ├── openapi.yaml               # REST API specification
│   ├── color.png                  # Agent icon (192x192)
│   └── outline.png                # Agent outline icon (32x32)
├── bridge_server/                 # FastAPI REST and MCP Bridge
│   ├── server.py
│   ├── circuitrf_client.py
│   ├── report_generator.py
│   └── excel_generator.py
├── rf_engine/                     # Friis cascade, matching, and defence specs
├── scripts/
│   ├── start_bridge.bat           # Windows launcher
│   ├── start_bridge.sh            # Linux launcher
│   ├── package_agent.py           # Generates circuitrf-copilot-agent.zip
│   └── test_workflow.py           # Verification suite
└── circuitrf-copilot-agent.zip    # Pre-packaged zip for sideloading
```

---

## 3. Step-by-Step Setup on Windows Work PC

### Step 3.1: Start the Local CircuitRF Bridge Server
Open Command Prompt or PowerShell in the project directory:
```cmd
cd C:\Users\<Username>\Documents\Code\dev\agent
scripts\start_bridge.bat
```
This automatically:
- Creates a virtual environment in `venv` if not already present.
- Installs dependencies from `requirements.txt`.
- Starts the FastAPI bridge on `http://127.0.0.1:8000`.
- Verifies interactive API docs at `http://127.0.0.1:8000/docs`.

### Step 3.2: Expose the Bridge Endpoint to Microsoft 365 Copilot
Because M365 Copilot runs in the Microsoft Cloud, it reaches your local workstation actions via an encrypted HTTPS tunnel:

Using **Microsoft Dev Tunnels** (Recommended for enterprise compliance):
```cmd
# 1. Login with your Microsoft Work Account
devtunnel user login

# 2. Host port 8000 anonymously or authenticated
devtunnel host -p 8000 --allow-anonymous
```
You will receive a public URL, for example:
`https://abc123xyz-8000.asse.devtunnels.ms`

Update `appPackage/openapi.yaml` servers entry:
```yaml
servers:
  - url: https://abc123xyz-8000.asse.devtunnels.ms
    description: Dev Tunnel to Windows Workstation Bridge
```

Re-run the packager:
```cmd
python scripts\package_agent.py
```
This updates `circuitrf-copilot-agent.zip`.

---

## 4. Deploying the Agent into Microsoft 365 Copilot

You can install the agent using any of the following three standard Microsoft deployment methods:

### Method A: Microsoft Teams Developer Portal (Easiest)
1. Open the [Teams Developer Portal](https://dev.teams.microsoft.com/) in your browser.
2. Sign in with your M365 work account.
3. Click on **Apps** in the left navigation sidebar.
4. Click **Import app**.
5. Select `circuitrf-copilot-agent.zip` from your project folder.
6. Click **Preview in Teams** or **Publish to Org / Sideload**.
7. Open **Microsoft 365 Copilot** (via Teams or [m365.cloud.microsoft/chat](https://m365.cloud.microsoft/chat)).
8. The **CircuitRF Agent** will appear under **Agents** in the right-hand panel!

### Method B: Microsoft Copilot Studio
1. Open [Microsoft Copilot Studio](https://copilotstudio.microsoft.com/).
2. Click **Create** > **New Copilot / Agent**.
3. Select **Import Declarative Agent package**.
4. Upload `circuitrf-copilot-agent.zip`.
5. Review the persona instructions, conversation starters, and action triggers.
6. Click **Publish** to make it active across your enterprise M365 Copilot experience.

### Method C: Microsoft 365 Admin Center (IT Administrator)
1. In the Microsoft 365 Admin Center, navigate to **Settings** > **Integrated apps**.
2. Click **Upload custom apps**.
3. Select **Teams app** (M365 Agent format) and upload `circuitrf-copilot-agent.zip`.
4. Assign permissions to your user account or engineering team.

---

## 5. Verifying the Agent in M365 Copilot

1. Open Microsoft 365 Copilot.
2. Select **CircuitRF Aerospace & Defence Agent** from the Copilot Agents list.
3. Try one of the conversation starters or prompt:
   > *"Synthesize an X-Band 10 GHz Bandpass Filter with 1 GHz bandwidth, run CircuitRF S-parameter simulation, and generate a Word engineering report and Excel spreadsheet."*
4. Copilot will:
   - Deconstruct requirements into incremental steps.
   - Call the `synthesizeNetlist` and `runSimulation` actions.
   - Run Friis cascaded Noise Figure and linearity checks.
   - Call `generateDocxReport` and `generateXlsxReport`.
   - Provide file paths and direct links to the generated engineering deliverables on your PC.

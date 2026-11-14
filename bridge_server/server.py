"""
FastAPI Bridge Server for Microsoft 365 Copilot Agent.
Exposes REST endpoints consumed by M365 Copilot Actions / Declarative Plugins,
orchestrating CircuitRF simulation, Friis cascade analysis, Word report generation,
and Excel workbook export.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project paths are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from rf_engine.cascade import RFStage, calculate_cascaded_chain
from rf_engine.matching import design_l_match, design_attenuator_pad
from rf_engine.military_specs import FREQUENCY_BANDS, evaluate_rf_margins
from rf_engine.netlist_builder import CircuitRFNetlistBuilder, build_attenuator_pad_cnl, build_bandpass_filter_cnl
from bridge_server.circuitrf_client import CircuitRFClient
from bridge_server.report_generator import RFReportGenerator
from bridge_server.excel_generator import RFExcelGenerator

app = FastAPI(
    title="M365 Copilot CircuitRF Aerospace Agent Bridge",
    description="REST API and MCP connector bridge for Defence & Aerospace RF component design, CircuitRF simulation, and Office automation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

circuit_client = CircuitRFClient(workspace_dir=os.path.join(BASE_DIR, "circuitrf_workspace"))
report_gen = RFReportGenerator(output_dir=os.path.join(BASE_DIR, "output_reports"))
excel_gen = RFExcelGenerator(output_dir=os.path.join(BASE_DIR, "output_reports"))

# --- Request / Response Models ---

class DecomposeRequest(BaseModel):
    title: str = Field(..., description="Project or Subsystem Title")
    frequency_band: str = Field(..., description="Target band (e.g. X-Band, S-Band, Ku-Band)")
    f0_ghz: float = Field(..., description="Center frequency in GHz")
    bw_ghz: float = Field(..., description="Operating bandwidth in GHz")
    min_gain_db: float = Field(20.0, description="Minimum overall gain requirement in dB")
    max_nf_db: float = Field(2.5, description="Maximum cascaded noise figure in dB")
    min_oip3_dbm: float = Field(30.0, description="Minimum output IP3 in dBm")
    application: str = Field("Airborne Radar Front-End", description="Defence or aerospace mission profile")

class NetlistRequest(BaseModel):
    circuit_type: str = Field("bandpass_filter", description="Topology: 'bandpass_filter', 'pi_pad', 'custom'")
    name: str = Field("Filter_Stage_1", description="Circuit identifier")
    f0_ghz: float = Field(10.0, description="Center frequency in GHz")
    bw_ghz: float = Field(1.0, description="Bandwidth in GHz")
    attenuation_db: Optional[float] = Field(6.0, description="For attenuator pads")

class SimulateRequest(BaseModel):
    netlist_content: Optional[str] = Field(None, description="CircuitRF .cnl netlist text")
    netlist_path: Optional[str] = Field(None, description="Path to existing .cnl file")
    start_ghz: float = Field(8.0, description="Sweep start frequency in GHz")
    stop_ghz: float = Field(12.0, description="Sweep stop frequency in GHz")
    npts: int = Field(101, description="Sweep point count")

class CascadeRequest(BaseModel):
    stages: List[Dict[str, Any]] = Field(..., description="List of RF stages with gain_db, nf_db, oip3_dbm, p1db_dbm")

class ReportRequest(BaseModel):
    project_title: str
    frequency_band: str
    requirements: Dict[str, Any]
    simulation_results: Dict[str, Any]
    cascaded_metrics: Optional[Dict[str, Any]] = None
    compliance_matrix: Optional[List[Dict[str, Any]]] = None
    convert_to_pdf: bool = False

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "M365 Copilot CircuitRF Bridge",
        "workspace": BASE_DIR,
        "circuitrf_mcp_ready": True
    }

@app.post("/api/rf/decompose")
def decompose_requirements(req: DecomposeRequest):
    """
    Interprets top-level RF requirements and produces an incremental execution plan,
    initial stage budgeting, and aerospace environmental constraints.
    """
    band_info = FREQUENCY_BANDS.get(req.frequency_band, {"range_ghz": (req.f0_ghz * 0.9, req.f0_ghz * 1.1), "typical_applications": req.application})
    
    # Calculate recommended stage architecture
    pre_filter_loss = 1.2
    lna_gain = req.min_gain_db + 2.0
    lna_nf = max(0.8, req.max_nf_db - 0.5)
    post_filter_loss = 1.5

    stages = [
        {"name": "Pre-Select Bandpass Filter", "stage_type": "Filter", "gain_db": -pre_filter_loss, "nf_db": pre_filter_loss, "oip3_dbm": 60.0, "p1db_dbm": 40.0, "v_dc": 0, "i_dc_ma": 0},
        {"name": "Primary Low Noise Amplifier", "stage_type": "LNA", "gain_db": lna_gain, "nf_db": lna_nf, "oip3_dbm": req.min_oip3_dbm - 5.0, "p1db_dbm": 15.0, "v_dc": 5.0, "i_dc_ma": 60.0},
        {"name": "Interstage Image Filter", "stage_type": "Filter", "gain_db": -post_filter_loss, "nf_db": post_filter_loss, "oip3_dbm": 60.0, "p1db_dbm": 40.0, "v_dc": 0, "i_dc_ma": 0}
    ]

    rf_stages = [RFStage(**s) for s in stages]
    budget = calculate_cascaded_chain(rf_stages)

    incremental_steps = [
        {"step": 1, "action": "Requirement Ingestion & De-rating", "details": f"Apply MIL-STD-883 and DO-160G thermal envelopes (-55C to +125C)."},
        {"step": 2, "action": "Passive Filter Synthesis", "details": f"Design {req.f0_ghz} GHz bandpass pre-selector with {req.bw_ghz} GHz BW in CircuitRF."},
        {"step": 3, "action": "Active LNA Matching & Stability", "details": f"Simulate input/output matching networks and confirm S11 < -15 dB."},
        {"step": 4, "action": "Cascaded Verification", "details": "Verify Friis noise figure and linearity margins against overall targets."},
        {"step": 5, "action": "Deliverable Compilation", "details": "Generate Word engineering memorandum (.docx) and multi-tab Excel budget (.xlsx)."}
    ]

    return {
        "project_title": req.title,
        "band": req.frequency_band,
        "band_info": band_info,
        "incremental_execution_plan": incremental_steps,
        "preliminary_stages": stages,
        "preliminary_cascaded_budget": budget
    }

@app.post("/api/rf/synthesize_netlist")
def synthesize_netlist(req: NetlistRequest):
    """
    Synthesizes CircuitRF .cnl netlist for common RF topologies.
    """
    if req.circuit_type == "bandpass_filter":
        cnl_text = build_bandpass_filter_cnl(req.name, req.f0_ghz, req.bw_ghz)
    elif req.circuit_type == "pi_pad":
        pad_calc = design_attenuator_pad(req.attenuation_db or 6.0)
        cnl_text = build_attenuator_pad_cnl(
            req.name,
            pad_calc["r_series_ohm"],
            pad_calc["r_shunt1_ohm"],
            pad_calc["r_shunt2_ohm"]
        )
    else:
        builder = CircuitRFNetlistBuilder(title=req.name)
        builder.add_port("P1", "in", "0", 1, 50.0)
        builder.add_port("P2", "out", "0", 2, 50.0)
        builder.add_sparam_analysis("SP1", 1.0, 18.0, 101)
        cnl_text = builder.build()

    # Save to disk
    cnl_path = os.path.join(circuit_client.workspace_dir, f"{req.name}.cnl")
    with open(cnl_path, "w", encoding="utf-8") as f:
        f.write(cnl_text)

    return {
        "circuit_name": req.name,
        "saved_path": cnl_path,
        "netlist_content": cnl_text
    }

@app.post("/api/rf/simulate")
def run_simulation(req: SimulateRequest):
    """
    Executes frequency sweep simulation via CircuitRF client.
    """
    if req.netlist_content:
        temp_cnl = os.path.join(circuit_client.workspace_dir, "sim_target.cnl")
        with open(temp_cnl, "w", encoding="utf-8") as f:
            f.write(req.netlist_content)
        cnl_path = temp_cnl
    elif req.netlist_path and os.path.exists(req.netlist_path):
        cnl_path = req.netlist_path
    else:
        raise HTTPException(status_code=400, detail="Provide netlist_content or a valid netlist_path.")

    # Syntax check
    chk = circuit_client.check_netlist(cnl_path)
    if not chk["success"]:
        return {"success": False, "stage": "check", "errors": chk["errors"]}

    # S-param run
    sim_res = circuit_client.run_sparam(
        cnl_path=cnl_path,
        start_ghz=req.start_ghz,
        stop_ghz=req.stop_ghz,
        npts=req.npts
    )
    return sim_res

@app.post("/api/rf/cascade")
def calculate_cascade(req: CascadeRequest):
    """
    Evaluates cascaded Friis Noise Figure, Gain, OIP3, P1dB, and DC consumption.
    """
    stages = [RFStage(**s) for s in req.stages]
    return calculate_cascaded_chain(stages)

@app.post("/api/report/docx")
def generate_docx(req: ReportRequest):
    """
    Compiles defence-standard Word report with embedded plots and tables.
    """
    docx_path = report_gen.generate_docx_report(
        project_title=req.project_title,
        frequency_band=req.frequency_band,
        requirements=req.requirements,
        simulation_results=req.simulation_results,
        cascaded_metrics=req.cascaded_metrics,
        compliance_matrix=req.compliance_matrix
    )
    pdf_path = None
    if req.convert_to_pdf:
        pdf_path = report_gen.convert_to_pdf_via_libreoffice(docx_path)

    return {
        "success": True,
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "filename": os.path.basename(docx_path)
    }

@app.post("/api/report/xlsx")
def generate_xlsx(req: ReportRequest):
    """
    Generates multi-tab Excel workbook with compliance, cascaded budget, and S-parameters.
    """
    xlsx_path = excel_gen.generate_xlsx_workbook(
        project_title=req.project_title,
        frequency_band=req.frequency_band,
        requirements=req.requirements,
        simulation_results=req.simulation_results,
        cascaded_metrics=req.cascaded_metrics,
        compliance_matrix=req.compliance_matrix
    )
    return {
        "success": True,
        "xlsx_path": xlsx_path,
        "filename": os.path.basename(xlsx_path)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

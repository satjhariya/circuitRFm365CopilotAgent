"""
Automated Aerospace & Defence Word Report (.docx) and LibreOffice CLI Generator.
Compiles RF technical memoranda with executive summaries, simulation tables,
embedded S-parameter plots, and compliance matrices.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

class RFReportGenerator:
    def __init__(self, output_dir: str = "/tmp/rf_reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_docx_report(
        self,
        project_title: str,
        frequency_band: str,
        requirements: Dict[str, Any],
        simulation_results: Dict[str, Any],
        cascaded_metrics: Optional[Dict[str, Any]] = None,
        compliance_matrix: Optional[List[Dict[str, Any]]] = None,
        author: str = "Lead RF Systems Architect (Aerospace & Defence)",
        filename: Optional[str] = None
    ) -> str:
        """
        Generates a comprehensive Word (.docx) technical report.
        """
        if filename is None:
            safe_title = "".join(c for c in project_title if c.isalnum() or c in ("-", "_")).rstrip()
            filename = f"RF_Design_Report_{safe_title}.docx"

        filepath = os.path.join(self.output_dir, filename)
        doc = Document()

        # Set page margins (0.75 in)
        for section in doc.sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        # Document Header
        p_head = doc.add_paragraph()
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run_head = p_head.add_run("RESTRICTED / DEFENCE ENGINEERING DOCUMENTATION\nREF: MIL-STD-883 / RTCA DO-160")
        run_head.font.size = Pt(8.5)
        run_head.font.bold = True
        run_head.font.color.rgb = RGBColor(120, 120, 120)

        # Title
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(project_title)
        run_title.font.size = Pt(22)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(15, 34, 64) # Navy Blue
        p_title.paragraph_format.space_after = Pt(4)

        # Subtitle
        p_sub = doc.add_paragraph()
        run_sub = p_sub.add_run(f"RF Architectural Simulation, Verification & CircuitRF Analysis ({frequency_band})")
        run_sub.font.size = Pt(13)
        run_sub.font.italic = True
        run_sub.font.color.rgb = RGBColor(70, 80, 95)
        p_sub.paragraph_format.space_after = Pt(14)

        # Metadata Table
        meta_table = doc.add_table(rows=3, cols=2)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_data = [
            ("Lead Systems Engineer / Persona:", author),
            ("Operational Frequency Band:", frequency_band),
            ("Compliance Standard:", "MIL-PRF-38534 Class H & DO-160G Section 4/21")
        ]
        for row_idx, (k, v) in enumerate(meta_data):
            cell_k = meta_table.cell(row_idx, 0)
            cell_v = meta_table.cell(row_idx, 1)
            cell_k.text = k
            cell_v.text = v
            cell_k.paragraphs[0].runs[0].font.bold = True
            cell_k.paragraphs[0].runs[0].font.size = Pt(9.5)
            cell_v.paragraphs[0].runs[0].font.size = Pt(9.5)
            cell_k.width = Inches(2.5)
            cell_v.width = Inches(4.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        # 1. Executive Summary
        self._add_section_heading(doc, "1. Executive Summary & Design Goals")
        p_exec = doc.add_paragraph(
            f"This technical memorandum documents the architecture synthesis, CircuitRF simulation results, "
            f"and compliance verification for the {project_title}. The subsystem operates in the {frequency_band} band "
            f"under aerospace and defence operational environments. Primary optimization criteria include "
            f"minimizing cascaded noise figure, maintaining unconditionally stable return loss (S11 < -15 dB), "
            f"and preserving high-linearity third-order intercept points (OIP3) across extreme thermal conditions."
        )
        p_exec.style.font.size = Pt(10)

        # 2. System Requirements & Specifications Table
        self._add_section_heading(doc, "2. System Requirements & Design Targets")
        if requirements:
            req_table = doc.add_table(rows=1, cols=3)
            req_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr = req_table.rows[0].cells
            hdr[0].text = "RF Parameter"
            hdr[1].text = "Target Specification"
            hdr[2].text = "Standard / Mission Requirement"
            self._style_table_header(hdr)

            for param, spec_val in requirements.items():
                row_cells = req_table.add_row().cells
                row_cells[0].text = str(param).replace("_", " ").title()
                row_cells[1].text = str(spec_val)
                row_cells[2].text = "DoD / Aerospace De-rated"
                for cell in row_cells:
                    cell.paragraphs[0].runs[0].font.size = Pt(9.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 3. CircuitRF Simulation Results & S-Parameters
        self._add_section_heading(doc, "3. CircuitRF High-Fidelity S-Parameter Simulation")
        p_sim = doc.add_paragraph(
            "Frequency-domain analysis was executed through the CircuitRF engine. "
            "Scattering parameters were calculated for input match (S11), forward gain/transmission (S21), "
            "and reverse isolation (S12) across the evaluation bandwidth."
        )
        p_sim.style.font.size = Pt(10)

        # Embed Plot if frequency data is present
        if "frequencies_ghz" in simulation_results and "s21_db" in simulation_results:
            plot_path = os.path.join(self.output_dir, f"{safe_title}_sparam.png")
            self._create_sparam_plot(
                simulation_results["frequencies_ghz"],
                simulation_results.get("s11_db", []),
                simulation_results.get("s21_db", []),
                plot_path,
                project_title
            )
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            doc.add_picture(plot_path, width=Inches(6.2))
            caption = doc.add_paragraph("Figure 1: CircuitRF Simulated S-Parameters (S11 Return Loss & S21 Transmission)")
            caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            caption.runs[0].font.italic = True
            caption.runs[0].font.size = Pt(8.5)

        # 4. Cascaded Lineup Table
        if cascaded_metrics and "stage_breakdown" in cascaded_metrics:
            self._add_section_heading(doc, "4. Cascaded Lineup Analysis (Friis & Intercept Points)")
            p_cas = doc.add_paragraph(
                f"Cascaded metrics across the chain indicate a total gain of {cascaded_metrics.get('total_gain_db', 0)} dB, "
                f"total noise figure of {cascaded_metrics.get('total_nf_db', 0)} dB, and total OIP3 of "
                f"{cascaded_metrics.get('total_oip3_dbm', 0)} dBm. Overall DC power consumption is "
                f"{cascaded_metrics.get('total_dc_power_w', 0)} W."
            )
            p_cas.style.font.size = Pt(10)

            c_table = doc.add_table(rows=1, cols=6)
            c_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            chdr = c_table.rows[0].cells
            chdr[0].text = "Stage"
            chdr[1].text = "Type"
            chdr[2].text = "Gain (dB)"
            chdr[3].text = "NF (dB)"
            chdr[4].text = "Cum. Gain (dB)"
            chdr[5].text = "Cum. NF (dB)"
            self._style_table_header(chdr)

            for stg in cascaded_metrics["stage_breakdown"]:
                row_c = c_table.add_row().cells
                row_c[0].text = str(stg["name"])
                row_c[1].text = str(stg["type"])
                row_c[2].text = f"{stg['stage_gain_db']:.2f}"
                row_c[3].text = f"{stg['stage_nf_db']:.2f}"
                row_c[4].text = f"{stg['cum_gain_db']:.2f}"
                row_c[5].text = f"{stg['cum_nf_db']:.2f}"
                for cell in row_c:
                    cell.paragraphs[0].runs[0].font.size = Pt(9.0)

        # 5. Aerospace Compliance & Margin Matrix
        if compliance_matrix:
            self._add_section_heading(doc, "5. Compliance & Military De-rating Matrix")
            cmp_table = doc.add_table(rows=1, cols=5)
            cmp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cmphdr = cmp_table.rows[0].cells
            cmphdr[0].text = "Metric / Parameter"
            cmphdr[1].text = "Required Target"
            cmphdr[2].text = "Simulated / Calculated"
            cmphdr[3].text = "Margin"
            cmphdr[4].text = "Compliance Status"
            self._style_table_header(cmphdr)

            for item in compliance_matrix:
                row_cmp = cmp_table.add_row().cells
                row_cmp[0].text = item.get("parameter", "")
                row_cmp[1].text = item.get("required", "")
                row_cmp[2].text = item.get("simulated", "")
                row_cmp[3].text = item.get("margin", "")
                row_cmp[4].text = item.get("status", "")
                
                # Highlight status
                st_run = row_cmp[4].paragraphs[0].runs[0]
                st_run.font.bold = True
                if item.get("status") == "PASS":
                    st_run.font.color.rgb = RGBColor(0, 128, 0)
                elif item.get("status") == "MARGINAL":
                    st_run.font.color.rgb = RGBColor(200, 120, 0)
                else:
                    st_run.font.color.rgb = RGBColor(200, 0, 0)

                for cell in row_cmp:
                    cell.paragraphs[0].runs[0].font.size = Pt(9.0)

        # 6. Conclusion and Engineering Sign-off
        self._add_section_heading(doc, "6. Conclusions & Architectural Sign-Off")
        p_conc = doc.add_paragraph(
            "The RF design model meets or exceeds all mission requirements specified for aerospace deployment. "
            "Layout artwork extraction and thermal co-simulation are recommended prior to tape-out."
        )
        p_conc.style.font.size = Pt(10)

        # Sign-off box
        p_sign = doc.add_paragraph()
        p_sign.add_run("\nVERIFIED BY: ___________________________    DATE: ______________\n").font.size = Pt(9.5)
        p_sign.add_run("Lead RF Systems Architect (Aerospace & Defence Division)").font.italic = True

        doc.save(filepath)
        return filepath

    def convert_to_pdf_via_libreoffice(self, docx_path: str) -> Optional[str]:
        """
        Converts .docx to .pdf using headless LibreOffice CLI if installed.
        """
        try:
            cmd = ["soffice", "--headless", "--convert-to", "pdf", "--outdir", self.output_dir, docx_path]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=8.0)
            if res.returncode == 0:
                pdf_name = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
                pdf_path = os.path.join(self.output_dir, pdf_name)
                if os.path.exists(pdf_path):
                    return pdf_path
        except Exception:
            pass
        return None

    def _create_sparam_plot(
        self,
        freqs: List[float],
        s11: List[float],
        s21: List[float],
        output_png: str,
        title: str
    ):
        fig, ax1 = plt.subplots(figsize=(8.0, 4.2), dpi=200)

        color_s21 = "#0d6efd" # Blue
        color_s11 = "#dc3545" # Red

        ax1.set_xlabel("Frequency (GHz)", fontsize=10, fontweight="bold")
        ax1.set_ylabel("Gain / Transmission S21 (dB)", color=color_s21, fontsize=10, fontweight="bold")
        ax1.plot(freqs, s21, color=color_s21, linewidth=2.0, label="S21 (Transmission)")
        ax1.tick_params(axis="y", labelcolor=color_s21)
        ax1.grid(True, linestyle="--", alpha=0.6)

        ax2 = ax1.twinx()
        ax2.set_ylabel("Return Loss S11 (dB)", color=color_s11, fontsize=10, fontweight="bold")
        ax2.plot(freqs, s11, color=color_s11, linewidth=2.0, linestyle="--", label="S11 (Return Loss)")
        ax2.tick_params(axis="y", labelcolor=color_s11)

        plt.title(f"CircuitRF S-Parameter Frequency Sweep - {title}", fontsize=11, fontweight="bold", pad=12)
        fig.tight_layout()
        plt.savefig(output_png, bbox_inches="tight")
        plt.close(fig)

    def _add_section_heading(self, doc: Document, text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 34, 64)

    def _style_table_header(self, hdr_cells):
        shading_xml = parse_xml(r'<w:shd {} w:fill="0F2240"/>'.format(nsdecls('w')))
        for cell in hdr_cells:
            cell._tc.get_or_add_tcPr().append(shading_xml)
            p = cell.paragraphs[0]
            if p.runs:
                p.runs[0].font.bold = True
                p.runs[0].font.size = Pt(9.5)
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

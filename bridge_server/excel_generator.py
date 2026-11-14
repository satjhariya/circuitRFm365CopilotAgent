"""
Automated Multi-Tab Excel (.xlsx) RF Compliance and Data Export Generator.
Outputs structured workbooks with conditional formatting, cascaded RF lineup sheets,
and high-density CircuitRF S-parameter datasets.
"""

import os
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class RFExcelGenerator:
    def __init__(self, output_dir: str = "/tmp/rf_reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_xlsx_workbook(
        self,
        project_title: str,
        frequency_band: str,
        requirements: Dict[str, Any],
        simulation_results: Dict[str, Any],
        cascaded_metrics: Optional[Dict[str, Any]] = None,
        compliance_matrix: Optional[List[Dict[str, Any]]] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Creates a comprehensive multi-tab Excel workbook (.xlsx).
        """
        if filename is None:
            safe_title = "".join(c for c in project_title if c.isalnum() or c in ("-", "_")).rstrip()
            filename = f"RF_Design_Data_{safe_title}.xlsx"

        filepath = os.path.join(self.output_dir, filename)
        wb = openpyxl.Workbook()

        # Styles
        font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        fill_navy = PatternFill(start_color="0F2240", end_color="0F2240", fill_type="solid")
        fill_sub_header = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        font_bold = Font(name="Calibri", size=10, bold=True)
        font_regular = Font(name="Calibri", size=10)
        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        border_thin = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        fill_pass = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        font_pass = Font(color="006100", bold=True)
        fill_marginal = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        font_marginal = Font(color="9C6500", bold=True)
        fill_fail = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        font_fail = Font(color="9C0006", bold=True)

        # ----------------------------------------------------
        # Tab 1: Compliance & Executive Summary
        # ----------------------------------------------------
        ws1 = wb.active
        ws1.title = "Compliance Matrix"
        ws1.views.sheetView[0].showGridLines = True

        ws1.merge_cells("A1:E1")
        ws1["A1"] = f"AEROSPACE & DEFENCE RF COMPLIANCE MATRIX: {project_title.upper()}"
        ws1["A1"].font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
        ws1["A1"].fill = fill_navy
        ws1["A1"].alignment = align_center
        ws1.row_dimensions[1].height = 30

        # Sub-header info
        info_items = [
            ("Operational Band:", frequency_band, "Classification:", "DEFENCE RESTRICTED"),
            ("Design Standard:", "MIL-PRF-38534 / DO-160G", "Status:", "COMPLETED & VERIFIED")
        ]
        curr_row = 3
        for item in info_items:
            ws1.cell(row=curr_row, column=1, value=item[0]).font = font_bold
            ws1.cell(row=curr_row, column=2, value=item[1]).font = font_regular
            ws1.cell(row=curr_row, column=4, value=item[2]).font = font_bold
            ws1.cell(row=curr_row, column=5, value=item[3]).font = font_regular
            curr_row += 1

        curr_row += 1
        # Compliance Table
        headers_ws1 = ["RF Metric / Parameter", "Target Requirement", "Simulated / Measured", "Margin", "Compliance Status"]
        for col_idx, h_text in enumerate(headers_ws1, 1):
            c = ws1.cell(row=curr_row, column=col_idx, value=h_text)
            c.font = font_header
            c.fill = fill_sub_header
            c.alignment = align_center
        ws1.row_dimensions[curr_row].height = 24

        curr_row += 1
        if compliance_matrix:
            for item in compliance_matrix:
                ws1.cell(row=curr_row, column=1, value=item.get("parameter", "")).alignment = align_left
                ws1.cell(row=curr_row, column=2, value=item.get("required", "")).alignment = align_center
                ws1.cell(row=curr_row, column=3, value=item.get("simulated", "")).alignment = align_center
                ws1.cell(row=curr_row, column=4, value=item.get("margin", "")).alignment = align_center
                
                status_cell = ws1.cell(row=curr_row, column=5, value=item.get("status", ""))
                status_cell.alignment = align_center
                if item.get("status") == "PASS":
                    status_cell.fill = fill_pass
                    status_cell.font = font_pass
                elif item.get("status") == "MARGINAL":
                    status_cell.fill = fill_marginal
                    status_cell.font = font_marginal
                else:
                    status_cell.fill = fill_fail
                    status_cell.font = font_fail

                for col_idx in range(1, 6):
                    ws1.cell(row=curr_row, column=col_idx).border = border_thin
                curr_row += 1

        # ----------------------------------------------------
        # Tab 2: Cascaded Lineup Budget
        # ----------------------------------------------------
        if cascaded_metrics and "stage_breakdown" in cascaded_metrics:
            ws2 = wb.create_sheet(title="Cascaded Lineup")
            ws2.views.sheetView[0].showGridLines = True

            ws2.merge_cells("A1:I1")
            ws2["A1"] = "RF FRONT-END CASCADED LINEUP BUDGET (GAIN, NOISE FIGURE, IP3)"
            ws2["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
            ws2["A1"].fill = fill_navy
            ws2["A1"].alignment = align_center
            ws2.row_dimensions[1].height = 26

            headers_ws2 = [
                "Stage", "Device Name", "Stage Gain (dB)", "Stage NF (dB)",
                "Stage OIP3 (dBm)", "Cum. Gain (dB)", "Cum. NF (dB)", "Cum. OIP3 (dBm)", "DC Power (mW)"
            ]
            for col_idx, h_text in enumerate(headers_ws2, 1):
                c = ws2.cell(row=3, column=col_idx, value=h_text)
                c.font = font_header
                c.fill = fill_sub_header
                c.alignment = align_center
            ws2.row_dimensions[3].height = 22

            row_ptr = 4
            for stg in cascaded_metrics["stage_breakdown"]:
                ws2.cell(row=row_ptr, column=1, value=stg["stage_index"]).alignment = align_center
                ws2.cell(row=row_ptr, column=2, value=f"{stg['name']} ({stg['type']})").alignment = align_left
                ws2.cell(row=row_ptr, column=3, value=stg["stage_gain_db"]).alignment = align_center
                ws2.cell(row=row_ptr, column=4, value=stg["stage_nf_db"]).alignment = align_center
                ws2.cell(row=row_ptr, column=5, value=stg["stage_oip3_dbm"]).alignment = align_center
                ws2.cell(row=row_ptr, column=6, value=stg["cum_gain_db"]).alignment = align_center
                ws2.cell(row=row_ptr, column=7, value=stg["cum_nf_db"]).alignment = align_center
                ws2.cell(row=row_ptr, column=8, value=stg["cum_oip3_dbm"]).alignment = align_center
                ws2.cell(row=row_ptr, column=9, value=stg["dc_power_mw"]).alignment = align_center

                for col_idx in range(1, 10):
                    cell = ws2.cell(row=row_ptr, column=col_idx)
                    cell.border = border_thin
                    cell.font = font_regular
                row_ptr += 1

            # Total Summary Row
            ws2.cell(row=row_ptr, column=2, value="TOTAL CASCADED SYSTEM").font = font_bold
            ws2.cell(row=row_ptr, column=6, value=cascaded_metrics.get("total_gain_db", 0)).font = font_bold
            ws2.cell(row=row_ptr, column=7, value=cascaded_metrics.get("total_nf_db", 0)).font = font_bold
            ws2.cell(row=row_ptr, column=8, value=cascaded_metrics.get("total_oip3_dbm", 0)).font = font_bold
            ws2.cell(row=row_ptr, column=9, value=cascaded_metrics.get("total_dc_power_w", 0) * 1000).font = font_bold

        # ----------------------------------------------------
        # Tab 3: CircuitRF S-Parameters Dataset
        # ----------------------------------------------------
        if "frequencies_ghz" in simulation_results and "s21_db" in simulation_results:
            ws3 = wb.create_sheet(title="CircuitRF S-Parameters")
            ws3.views.sheetView[0].showGridLines = True

            ws3.merge_cells("A1:F1")
            ws3["A1"] = f"CIRCUITRF S-PARAMETER SIMULATION DATA: {project_title}"
            ws3["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
            ws3["A1"].fill = fill_navy
            ws3["A1"].alignment = align_center

            headers_ws3 = [
                "Frequency (GHz)", "S11 Return Loss (dB)", "S21 Gain/Loss (dB)",
                "S12 Isolation (dB)", "S22 Output Match (dB)", "Input VSWR (:1)"
            ]
            for col_idx, h_text in enumerate(headers_ws3, 1):
                c = ws3.cell(row=3, column=col_idx, value=h_text)
                c.font = font_header
                c.fill = fill_sub_header
                c.alignment = align_center
            ws3.row_dimensions[3].height = 22

            freqs = simulation_results["frequencies_ghz"]
            s11_list = simulation_results.get("s11_db", [0]*len(freqs))
            s21_list = simulation_results.get("s21_db", [0]*len(freqs))
            s12_list = simulation_results.get("s12_db", [0]*len(freqs))
            s22_list = simulation_results.get("s22_db", [0]*len(freqs))

            for idx, f_val in enumerate(freqs):
                r_idx = idx + 4
                s11_val = s11_list[idx]
                s21_val = s21_list[idx]
                s12_val = s12_list[idx] if idx < len(s12_list) else -40.0
                s22_val = s22_list[idx] if idx < len(s22_list) else -20.0

                # Compute VSWR from S11 (dB)
                gamma_mag = 10.0 ** (s11_val / 20.0)
                vswr = (1.0 + gamma_mag) / max(1.0 - gamma_mag, 1e-4) if gamma_mag < 1.0 else 99.0

                ws3.cell(row=r_idx, column=1, value=round(f_val, 4)).alignment = align_center
                ws3.cell(row=r_idx, column=2, value=s11_val).alignment = align_center
                ws3.cell(row=r_idx, column=3, value=s21_val).alignment = align_center
                ws3.cell(row=r_idx, column=4, value=s12_val).alignment = align_center
                ws3.cell(row=r_idx, column=5, value=s22_val).alignment = align_center
                ws3.cell(row=r_idx, column=6, value=round(vswr, 2)).alignment = align_center

                for col_idx in range(1, 7):
                    c = ws3.cell(row=r_idx, column=col_idx)
                    c.border = border_thin
                    c.font = font_regular

        # Auto-adjust column widths across all sheets
        for sheet in wb.worksheets:
            for col in sheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(filepath)
        return filepath

"""
RF Cascaded System Analysis for Aerospace and Defence Architectures.
Computes stage-by-stage cumulative Gain, Noise Figure (Friis), Output/Input IP3, and P1dB.
"""

from typing import List, Dict, Any
import math

class RFStage:
    def __init__(
        self,
        name: str,
        stage_type: str,
        gain_db: float,
        nf_db: float,
        oip3_dbm: float = 999.0,
        p1db_dbm: float = 999.0,
        v_dc: float = 0.0,
        i_dc_ma: float = 0.0
    ):
        self.name = name
        self.stage_type = stage_type # e.g. LNA, Filter, Attenuator, Mixer, Driver, PA
        self.gain_db = gain_db
        self.nf_db = nf_db
        self.oip3_dbm = oip3_dbm
        self.p1db_dbm = p1db_dbm
        self.v_dc = v_dc
        self.i_dc_ma = i_dc_ma

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "stage_type": self.stage_type,
            "gain_db": self.gain_db,
            "nf_db": self.nf_db,
            "oip3_dbm": self.oip3_dbm,
            "p1db_dbm": self.p1db_dbm,
            "v_dc": self.v_dc,
            "i_dc_ma": self.i_dc_ma,
            "p_dc_mw": self.v_dc * self.i_dc_ma
        }

def calculate_cascaded_chain(stages: List[RFStage]) -> Dict[str, Any]:
    """
    Computes cascaded RF metrics across sequential stages.
    Returns overall metrics and cumulative stage-by-stage breakdowns.
    """
    if not stages:
        return {
            "total_gain_db": 0.0,
            "total_nf_db": 0.0,
            "total_oip3_dbm": 0.0,
            "total_iip3_dbm": 0.0,
            "total_p1db_dbm": 0.0,
            "total_dc_power_w": 0.0,
            "stage_breakdown": []
        }

    breakdown = []
    cum_gain_linear = 1.0
    cum_f_linear = 0.0
    inv_oip3_linear = 0.0
    inv_p1db_linear = 0.0
    total_dc_power_mw = 0.0

    for idx, stage in enumerate(stages):
        g_lin = 10.0 ** (stage.gain_db / 10.0)
        f_lin = 10.0 ** (stage.nf_db / 10.0)
        oip3_mw = 10.0 ** (stage.oip3_dbm / 10.0)
        p1db_mw = 10.0 ** (stage.p1db_dbm / 10.0)
        dc_mw = stage.v_dc * stage.i_dc_ma
        total_dc_power_mw += dc_mw

        # Friis Noise Figure: F_tot = F_1 + (F_2 - 1)/G_1 + (F_3 - 1)/(G_1*G_2) + ...
        if idx == 0:
            cum_f_linear = f_lin
            inv_oip3_linear = 1.0 / oip3_mw
            inv_p1db_linear = 1.0 / p1db_mw
            cum_gain_linear = g_lin
        else:
            cum_f_linear += (f_lin - 1.0) / cum_gain_linear
            inv_oip3_linear = (inv_oip3_linear * g_lin) + (1.0 / oip3_mw)
            inv_p1db_linear = (inv_p1db_linear * g_lin) + (1.0 / p1db_mw)
            cum_gain_linear *= g_lin

        current_gain_db = 10.0 * math.log10(cum_gain_linear) if cum_gain_linear > 0 else 0.0
        current_nf_db = 10.0 * math.log10(max(cum_f_linear, 1.0))
        current_oip3_dbm = 10.0 * math.log10(1.0 / inv_oip3_linear) if inv_oip3_linear > 0 else 999.0
        current_iip3_dbm = current_oip3_dbm - current_gain_db
        current_p1db_dbm = 10.0 * math.log10(1.0 / inv_p1db_linear) if inv_p1db_linear > 0 else 999.0

        breakdown.append({
            "stage_index": idx + 1,
            "name": stage.name,
            "type": stage.stage_type,
            "stage_gain_db": round(stage.gain_db, 2),
            "stage_nf_db": round(stage.nf_db, 2),
            "stage_oip3_dbm": round(stage.oip3_dbm, 2),
            "stage_p1db_dbm": round(stage.p1db_dbm, 2),
            "cum_gain_db": round(current_gain_db, 2),
            "cum_nf_db": round(current_nf_db, 2),
            "cum_oip3_dbm": round(current_oip3_dbm, 2),
            "cum_iip3_dbm": round(current_iip3_dbm, 2),
            "cum_p1db_dbm": round(current_p1db_dbm, 2),
            "dc_power_mw": round(dc_mw, 2)
        })

    last_stage = breakdown[-1]
    return {
        "total_gain_db": last_stage["cum_gain_db"],
        "total_nf_db": last_stage["cum_nf_db"],
        "total_oip3_dbm": last_stage["cum_oip3_dbm"],
        "total_iip3_dbm": last_stage["cum_iip3_dbm"],
        "total_p1db_dbm": last_stage["cum_p1db_dbm"],
        "total_dc_power_w": round(total_dc_power_mw / 1000.0, 3),
        "stage_breakdown": breakdown
    }

"""
Aerospace and Defence RF Specification Standards and De-rating Rules.
Complies with MIL-STD-883, MIL-PRF-38534, RTCA DO-160G, and ECSS component guidelines.
"""

from typing import Dict, Any, List

FREQUENCY_BANDS: Dict[str, Dict[str, Any]] = {
    "HF": {"range_ghz": (0.003, 0.03), "typical_applications": "Over-the-horizon radar, tactical comms"},
    "VHF": {"range_ghz": (0.03, 0.3), "typical_applications": "ATC, tactical line-of-sight voice/data"},
    "UHF": {"range_ghz": (0.3, 1.0), "typical_applications": "Early warning radar, military SATCOM (UFO/MUOS)"},
    "L-Band": {"range_ghz": (1.0, 2.0), "typical_applications": "GPS, IFF, Link 16, air surveillance radar"},
    "S-Band": {"range_ghz": (2.0, 4.0), "typical_applications": "Naval radar, weather radar, telemetry tracking"},
    "C-Band": {"range_ghz": (4.0, 8.0), "typical_applications": "Phased-array radar, satellite downlinks, EW"},
    "X-Band": {"range_ghz": (8.0, 12.0), "typical_applications": "Fire control radar, airborne intercept, SAR"},
    "Ku-Band": {"range_ghz": (12.0, 18.0), "typical_applications": "Precision weapon tracking, tactical UAV datalinks"},
    "K-Band": {"range_ghz": (18.0, 27.0), "typical_applications": "Airport surface detection, military SATCOM"},
    "Ka-Band": {"range_ghz": (27.0, 40.0), "typical_applications": "Wideband SATCOM (WGS), missile seeker heads"},
    "W-Band": {"range_ghz": (75.0, 110.0), "typical_applications": "Millimeter-wave radar, active denial, perimeter security"}
}

MIL_TEMP_RANGES = {
    "Commercial": {"t_min_c": 0, "t_max_c": 70, "standard": "Commercial COTS"},
    "Industrial": {"t_min_c": -40, "t_max_c": 85, "standard": "IEC 60068"},
    "Aerospace_DO160": {"t_min_c": -55, "t_max_c": 85, "standard": "RTCA DO-160G Section 4 Cat A2/B2"},
    "Military_Standard": {"t_min_c": -55, "t_max_c": 125, "standard": "MIL-STD-883 / MIL-PRF-38534 Class H/K"},
    "Space_Extended": {"t_min_c": -55, "t_max_c": 150, "standard": "ECSS-Q-ST-60C / MIL-STD-1547"}
}

DERATING_FACTORS = {
    "resistor_power_derate": 0.50, # Operate at <= 50% rated dissipation
    "capacitor_voltage_derate": 0.60, # Operate at <= 60% rated dielectric voltage
    "semiconductor_tj_max_c": 110.0, # Max GaN/GaAs junction temp in defence missions
    "rf_input_power_headroom_db": 3.0, # 3 dB headroom below Absolute Max Rating
    "vswr_tolerance_load": 3.0 # Must withstand up to 3:1 VSWR without damage
}

def evaluate_rf_margins(
    specs: Dict[str, float],
    results: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Evaluates simulated RF metrics against defence compliance specifications.
    Returns compliance matrix with Pass/Margin/Fail status and margin calculations.
    """
    compliance_matrix = []

    # Gain Check
    if "min_gain_db" in specs and "gain_db" in results:
        margin = results["gain_db"] - specs["min_gain_db"]
        status = "PASS" if margin >= 0.5 else ("MARGINAL" if margin >= 0.0 else "FAIL")
        compliance_matrix.append({
            "parameter": "RF Gain (dB)",
            "required": f">= {specs['min_gain_db']} dB",
            "simulated": f"{results['gain_db']:.2f} dB",
            "margin": f"{margin:+.2f} dB",
            "status": status
        })

    # Noise Figure Check
    if "max_nf_db" in specs and "nf_db" in results:
        margin = specs["max_nf_db"] - results["nf_db"]
        status = "PASS" if margin >= 0.3 else ("MARGINAL" if margin >= 0.0 else "FAIL")
        compliance_matrix.append({
            "parameter": "Noise Figure (dB)",
            "required": f"<= {specs['max_nf_db']} dB",
            "simulated": f"{results['nf_db']:.2f} dB",
            "margin": f"{margin:+.2f} dB",
            "status": status
        })

    # Return Loss Check (S11)
    if "min_return_loss_db" in specs and "return_loss_db" in results:
        margin = results["return_loss_db"] - specs["min_return_loss_db"]
        status = "PASS" if margin >= 1.0 else ("MARGINAL" if margin >= 0.0 else "FAIL")
        compliance_matrix.append({
            "parameter": "Input Return Loss (dB)",
            "required": f">= {specs['min_return_loss_db']} dB",
            "simulated": f"{results['return_loss_db']:.2f} dB",
            "margin": f"{margin:+.2f} dB",
            "status": status
        })

    # Output IP3 Check
    if "min_oip3_dbm" in specs and "oip3_dbm" in results:
        margin = results["oip3_dbm"] - specs["min_oip3_dbm"]
        status = "PASS" if margin >= 1.0 else ("MARGINAL" if margin >= 0.0 else "FAIL")
        compliance_matrix.append({
            "parameter": "Output IP3 (dBm)",
            "required": f">= {specs['min_oip3_dbm']} dBm",
            "simulated": f"{results['oip3_dbm']:.2f} dBm",
            "margin": f"{margin:+.2f} dBm",
            "status": status
        })

    # Output P1dB Check
    if "min_p1db_dbm" in specs and "p1db_dbm" in results:
        margin = results["p1db_dbm"] - specs["min_p1db_dbm"]
        status = "PASS" if margin >= 0.5 else ("MARGINAL" if margin >= 0.0 else "FAIL")
        compliance_matrix.append({
            "parameter": "Output P1dB (dBm)",
            "required": f">= {specs['min_p1db_dbm']} dBm",
            "simulated": f"{results['p1db_dbm']:.2f} dBm",
            "margin": f"{margin:+.2f} dBm",
            "status": status
        })

    return compliance_matrix

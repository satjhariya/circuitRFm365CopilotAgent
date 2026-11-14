"""
Impedance matching and RF network utilities for CircuitRF integration.
Includes L-section, Pi-pad, T-pad, Quarter-wave transformers, and VSWR/Return-loss conversions.
"""

import math
import cmath
from typing import Dict, Any, Tuple

def gamma_to_vswr(gamma: complex) -> float:
    mag = abs(gamma)
    if mag >= 1.0:
        return 999.0
    return (1.0 + mag) / (1.0 - mag)

def gamma_to_return_loss_db(gamma: complex) -> float:
    mag = abs(gamma)
    if mag <= 1e-6:
        return 120.0
    return -20.0 * math.log10(mag)

def z_to_gamma(z: complex, z0: float = 50.0) -> complex:
    if z + z0 == 0:
        return complex(1.0, 0.0)
    return (z - z0) / (z + z0)

def gamma_to_z(gamma: complex, z0: float = 50.0) -> complex:
    if abs(1.0 - gamma) < 1e-9:
        return complex(1e9, 0.0)
    return z0 * (1.0 + gamma) / (1.0 - gamma)

def design_l_match(
    rs: float,
    rl: float,
    freq_hz: float,
    match_type: str = "lowpass"
) -> Dict[str, Any]:
    """
    Synthesize an L-section impedance match between Rs and RL at freq_hz.
    Low-pass: Series L, Shunt C.
    High-pass: Series C, Shunt L.
    """
    omega = 2.0 * math.pi * freq_hz
    if rs <= 0 or rl <= 0:
        raise ValueError("Rs and RL must be positive real values.")

    # Determine which resistance is larger
    r_high = max(rs, rl)
    r_low = min(rs, rl)
    q = math.sqrt((r_high / r_low) - 1.0)

    # Low-pass topology:
    # If Rs < RL: Series component at Rs side, Shunt component at RL side
    # X_series = Q * R_low
    # X_shunt = R_high / Q
    x_series = q * r_low
    x_shunt = r_high / q

    if match_type.lower() == "lowpass":
        # Series Inductor, Shunt Capacitor
        l_series_h = x_series / omega
        c_shunt_f = 1.0 / (omega * x_shunt)
        return {
            "topology": "Low-pass L-Match",
            "q_factor": round(q, 3),
            "freq_ghz": round(freq_hz / 1e9, 4),
            "series_component": {"type": "Inductor", "value_nh": round(l_series_h * 1e9, 3)},
            "shunt_component": {"type": "Capacitor", "value_pf": round(c_shunt_f * 1e12, 3)},
            "placed_on_low_z_side": "Series L on Rs" if rs < rl else "Series L on RL",
            "placed_on_high_z_side": "Shunt C on RL" if rs < rl else "Shunt C on Rs"
        }
    else:
        # High-pass: Series Capacitor, Shunt Inductor
        c_series_f = 1.0 / (omega * x_series)
        l_shunt_h = x_shunt / omega
        return {
            "topology": "High-pass L-Match",
            "q_factor": round(q, 3),
            "freq_ghz": round(freq_hz / 1e9, 4),
            "series_component": {"type": "Capacitor", "value_pf": round(c_series_f * 1e12, 3)},
            "shunt_component": {"type": "Inductor", "value_nh": round(l_shunt_h * 1e9, 3)},
            "placed_on_low_z_side": "Series C on Rs" if rs < rl else "Series C on RL",
            "placed_on_high_z_side": "Shunt L on RL" if rs < rl else "Shunt L on Rs"
        }

def design_attenuator_pad(attenuation_db: float, z0: float = 50.0, pad_type: str = "pi") -> Dict[str, Any]:
    """
    Design matched Pi-pad or T-pad attenuator for specified dB loss.
    """
    if attenuation_db <= 0:
        raise ValueError("Attenuation must be greater than 0 dB.")

    k = 10.0 ** (attenuation_db / 20.0) # Voltage ratio

    if pad_type.lower() == "pi":
        r_series = z0 * (k * k - 1.0) / (2.0 * k)
        r_shunt = z0 * (k + 1.0) / (k - 1.0)
        return {
            "type": "Pi-Pad Attenuator",
            "attenuation_db": attenuation_db,
            "z0_ohm": z0,
            "r_series_ohm": round(r_series, 2),
            "r_shunt1_ohm": round(r_shunt, 2),
            "r_shunt2_ohm": round(r_shunt, 2)
        }
    else:
        # T-Pad
        r_series = z0 * (k - 1.0) / (k + 1.0)
        r_shunt = z0 * (2.0 * k) / (k * k - 1.0)
        return {
            "type": "T-Pad Attenuator",
            "attenuation_db": attenuation_db,
            "z0_ohm": z0,
            "r_series1_ohm": round(r_series, 2),
            "r_series2_ohm": round(r_series, 2),
            "r_shunt_ohm": round(r_shunt, 2)
        }

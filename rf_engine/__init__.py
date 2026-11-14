"""
RF Engine package for Aerospace & Defence RF Architecture and CircuitRF Synthesis.
"""

from .cascade import RFStage, calculate_cascaded_chain
from .matching import design_l_match, design_attenuator_pad, gamma_to_vswr, gamma_to_return_loss_db
from .military_specs import FREQUENCY_BANDS, MIL_TEMP_RANGES, DERATING_FACTORS, evaluate_rf_margins
from .netlist_builder import CircuitRFNetlistBuilder, build_attenuator_pad_cnl, build_bandpass_filter_cnl

__all__ = [
    "RFStage",
    "calculate_cascaded_chain",
    "design_l_match",
    "design_attenuator_pad",
    "gamma_to_vswr",
    "gamma_to_return_loss_db",
    "FREQUENCY_BANDS",
    "MIL_TEMP_RANGES",
    "DERATING_FACTORS",
    "evaluate_rf_margins",
    "CircuitRFNetlistBuilder",
    "build_attenuator_pad_cnl",
    "build_bandpass_filter_cnl"
]

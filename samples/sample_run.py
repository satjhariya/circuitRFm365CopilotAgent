#!/usr/bin/env python3
"""
Quick demo execution script using pre-configured benchmark requirements.
Runs synthesis, simulation, cascaded analysis, and produces Word and Excel deliverables.
"""

import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.test_workflow import run_test

if __name__ == "__main__":
    print("Executing Sample Benchmark Run for M365 Copilot CircuitRF Agent...")
    run_test()

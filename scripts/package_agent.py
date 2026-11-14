#!/usr/bin/env python3
"""
Packages the M365 Copilot Declarative Agent into a deployable .zip package.
This zip file can be sideloaded into Microsoft 365 Copilot via:
- Microsoft Teams Developer Portal (portal.azure.com / dev.teams.microsoft.com)
- Microsoft 365 Admin Center (Settings > Integrated Apps)
- Microsoft Copilot Studio (Copilot Extensions / Declarative Agents)
"""

import os
import zipfile
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PACKAGE_DIR = os.path.join(BASE_DIR, "appPackage")
OUTPUT_ZIP = os.path.join(BASE_DIR, "circuitrf-copilot-agent.zip")

REQUIRED_FILES = [
    "manifest.json",
    "declarativeAgent.json",
    "ai-plugin.json",
    "openapi.yaml",
    "color.png",
    "outline.png"
]

def create_agent_package():
    print(f"Creating M365 Copilot Agent Package from {APP_PACKAGE_DIR}...")
    
    missing = [f for f in REQUIRED_FILES if not os.path.exists(os.path.join(APP_PACKAGE_DIR, f))]
    if missing:
        print(f"Error: Missing required package files: {missing}", file=sys.stderr)
        sys.exit(1)

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in REQUIRED_FILES:
            filepath = os.path.join(APP_PACKAGE_DIR, filename)
            zip_file.write(filepath, arcname=filename)
            print(f"  + Added: {filename} ({os.path.getsize(filepath)} bytes)")

    print(f"\nSuccessfully generated package: {OUTPUT_ZIP}")
    print(f"Total size: {os.path.getsize(OUTPUT_ZIP)} bytes")
    print("\nReady for deployment into Microsoft 365 Copilot.")

if __name__ == "__main__":
    create_agent_package()

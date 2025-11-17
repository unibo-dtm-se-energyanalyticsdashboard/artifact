#!/usr/bin/env python
"""
This script serves as a direct, manual entry point for running the ingestion pipeline.

It is designed to be run from the root of the repository (e.g., `python scripts/ingest.py`).
It dynamically modifies the system path to ensure that the main 'edas' source package
(located in 'src/') can be imported.
"""

import argparse
import os
import sys

# --- Dynamic Path Configuration ---
# Calculate the project's root directory (one level up from 'scripts')
ROOT = os.path.dirname(os.path.dirname(__file__))
# Calculate the path to the main source code directory
SRC = os.path.join(ROOT, "src")

# Add the 'src' directory to the Python system path (sys.path)
# This allows the script to find and import modules from 'src/edas'
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# --- Import Application Components ---
# Import the main pipeline orchestrator (Application Service)
from edas.pipeline import run_pipeline
# Import the centralized logging setup
from edas.logging_config import setup_logging

# Configure the application's root logger
setup_logging("INFO")


def main():
    """
    Parses CLI arguments and executes the main ingestion pipeline.
    """
    # Initialize the argument parser
    p = argparse.ArgumentParser(description="ENTSO-E ingestion pipeline")
    
    # Define command-line arguments
    p.add_argument(
        "--countries", 
        nargs="+", 
        default=["FR", "DE"], 
        help="List of country codes (e.g., FR DE)"
    )
    p.add_argument(
        "--mode", 
        choices=["full_2025", "last_10_days"], 
        default="last_10_days",
        help="The time range mode for data fetching."
    )
    p.add_argument(
        "--no-flows", 
        action="store_true", 
        help="If set, skips the ingestion of cross-border flows."
    )
    args = p.parse_args()

    # Call the main pipeline function from the 'edas' package
    run_pipeline(
        countries=args.countries,
        include_flows=(not args.no_flows), # Invert the "no-flows" flag
        mode=args.mode
    )

# Standard Python entry point
if __name__ == "__main__":
    main()
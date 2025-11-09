#!/usr/bin/env python
import argparse
import os, sys
ROOT = os.path.dirname(os.path.dirname(__file__))  
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from edas.pipeline import run_pipeline
from edas.logging_config import setup_logging


setup_logging("INFO")


def main():
    p = argparse.ArgumentParser(description="ENTSO-E ingestion pipeline")
    p.add_argument("--countries", nargs="+", default=["FR", "DE"], help="e.g., FR DE")
    p.add_argument("--mode", choices=["full_2025", "last_10_days"], default="last_10_days")
    p.add_argument("--no-flows", action="store_true", help="skip cross-border flows")
    args = p.parse_args()

    run_pipeline(
        countries=args.countries,
        include_flows=(not args.no_flows),
        mode=args.mode
    )

if __name__ == "__main__":
    main()

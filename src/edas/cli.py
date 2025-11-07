import argparse
from dotenv import load_dotenv

def ingest_main():
    """CLI entrypoint for data ingestion."""
    load_dotenv()

 
    p = argparse.ArgumentParser(prog="edas-ingest", description="ENTSO-E ingestion pipeline")
    p.add_argument("--mode", choices=["last_10_days", "full_2025", "custom"], default="last_10_days")
    p.add_argument("--start", help="YYYY-MM-DD (required if --mode custom)")
    p.add_argument("--end", help="YYYY-MM-DD (required if --mode custom)")
    p.add_argument("--countries", nargs="+", default=["FR", "DE"], help="e.g. FR DE")
    args = p.parse_args()

 
    from edas.pipeline import run_pipeline

    if args.mode == "custom" and (not args.start or not args.end):
        p.error("--start and --end are required when --mode=custom")

    try:
    
        run_pipeline(
            mode=args.mode,
            countries=args.countries,
            start=args.start,
            end=args.end,
        )
    except TypeError:
    
        run_pipeline(mode=args.mode, countries=args.countries)

def dashboard_main():
    """CLI entrypoint for Dash app."""
    from edas.dashboard.app import app
    # Dash 3.x
    app.run(host="127.0.0.1", port=8050, debug=True)

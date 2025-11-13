# src/edas/config.py
import os
from dotenv import load_dotenv

# Load variables from .env (if present)
load_dotenv()

# ENTSO-E API key (mandatory)
ENTSOE_API_KEY = os.getenv("ENTSOE_API_KEY")
if not ENTSOE_API_KEY:
    raise RuntimeError("Missing ENTSOE_API_KEY in environment/.env")

# Default timezone for ENTSO-E data
TZ_EUROPE = os.getenv("TZ_EUROPE", "Europe/Brussels")

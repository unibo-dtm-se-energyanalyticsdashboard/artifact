# src/edas/config.py

import os
from typing import Final

from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# -----------------------------
# ENTSO-E API configuration
# -----------------------------

_raw_key = os.getenv("ENTSOE_API_KEY")

ENTSOE_API_KEY: Final[str] = _raw_key or ""

# Default timezone for ENTSO-E data
TZ_EUROPE: Final[str] = "Europe/Brussels"

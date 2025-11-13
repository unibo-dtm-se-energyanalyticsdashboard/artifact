# src/edas/config.py

import os
from typing import Final

from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# -----------------------------
# ENTSO-E API configuration
# -----------------------------

ENTSOE_API_KEY: Final[str] = os.getenv("ENTSOE_API_KEY", "")

if not ENTSOE_API_KEY:
    raise RuntimeError(
        "ENTSOE_API_KEY is not set. Please define it in your .env file or environment."
    )

# Default timezone for ENTSO-E data
TZ_EUROPE: Final[str] = "Europe/Brussels"

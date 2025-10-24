# =======================================
# Global Configuration for EDAS Project
# =======================================

# API key for ENTSO-E Transparency Platform
ENTSOE_API_KEY = "df175bd8-e901-42d1-b3f1-7bb638056c94"

# Default timezone for ENTSO-E data
TZ_EUROPE = "Europe/Brussels"

# Database connection info
DB = {
    "user": "postgres",
    "password": "Password123",   # تغییر بده اگر در سیستم تو فرق داره
    "host": "localhost",
    "port": "5432",
    "database": "energy_analytics",
}

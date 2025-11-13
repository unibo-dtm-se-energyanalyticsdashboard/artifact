# =======================================
# Global Configuration for EDAS Project
# =======================================

# API key for ENTSO-E Transparency Platform
ENTSOE_API_KEY = "ad80a684-56b8-4229-9138-4099fbef344d"

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

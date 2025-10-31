import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()

def get_engine():
    """
    Create and return a SQLAlchemy engine for PostgreSQL using psycopg2.
    Reads all configuration from environment variables (.env).
    """
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]


    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing required environment variable: {var}")

    uri = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    return create_engine(uri, pool_pre_ping=True)

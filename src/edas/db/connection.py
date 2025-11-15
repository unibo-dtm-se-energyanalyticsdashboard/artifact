import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from a .env file (e.g., DB_USER, DB_PASSWORD)
# This allows for secure configuration management (Part of DevOps/Deployment best practices).
load_dotenv()

def get_engine():
    """
    Creates and returns a SQLAlchemy engine for PostgreSQL (Database Adapter).
    
    This function acts as a factory, centralizing the database connection logic.
    It securely reads all configuration from environment variables.
    
    Raises:
        EnvironmentError: If any required database environment variable is missing.
    
    Returns:
        sqlalchemy.engine.Engine: The configured SQLAlchemy engine (connection pool).
    """
    
    # Define the list of mandatory environment variables required for connection.
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]

    # Validate that all required environment variables are set.
    for var in required_vars:
        if not os.getenv(var):
            # Fail fast if configuration is incomplete.
            raise EnvironmentError(f"Missing required environment variable: {var}")

    # Construct the database connection URI (DSN) using the loaded env variables.
    # We specify 'postgresql+psycopg2' as the dialect.
    uri = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    # Create the SQLAlchemy engine.
    # 'pool_pre_ping=True' checks connection validity before use, preventing stale connections.
    return create_engine(uri, pool_pre_ping=True)
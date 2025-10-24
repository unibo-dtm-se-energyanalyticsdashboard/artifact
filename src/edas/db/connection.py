from sqlalchemy import create_engine
from edas.config import DB

def get_engine():
    """
    Returns a SQLAlchemy Engine using psycopg (v3) driver.
    """
    uri = (
        f"postgresql+psycopg://{DB['user']}:{DB['password']}"
        f"@{DB['host']}:{DB['port']}/{DB['database']}"
    )
    return create_engine(uri, pool_pre_ping=True)

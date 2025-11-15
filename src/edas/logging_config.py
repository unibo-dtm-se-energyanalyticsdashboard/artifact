import logging
# Import the specific handler for log rotation
from logging.handlers import RotatingFileHandler

def setup_logging(level: str = "INFO") -> None:
    """
    Configures the root logger for the entire application (idempotent).
    
    Sets up two handlers:
    1. StreamHandler: To log messages to the console (stderr).
    2. RotatingFileHandler: To log messages to a file with automatic rotation.
    
    Args:
        level: The minimum logging level to process (e.g., "INFO", "DEBUG").
    """
    # Get the root logger instance
    logger = logging.getLogger()
    
    # Idempotency check: If handlers are already configured, do nothing.
    # This prevents duplicate logs if this function is called multiple times.
    if logger.handlers:
        return

    # Set the minimum logging level on the root logger
    # Uses getattr to dynamically find the logging level (e.g., logging.INFO)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Define a standard format for all log messages
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    # --- Handler 1: Console (StreamHandler) ---
    stream_h = logging.StreamHandler()
    stream_h.setFormatter(formatter)

    # --- Handler 2: Rotating File (RotatingFileHandler) ---
    # This ensures log files don't grow indefinitely.
    file_h = RotatingFileHandler(
        "logs/app.log",         # Path to the log file (must match .gitignore)
        maxBytes=2_000_000,     # 2 MB per file
        backupCount=3,          # Keep 3 old log files (e.g., app.log.1, app.log.2)
        encoding="utf-8"
    )
    file_h.setFormatter(formatter)

    # Add both handlers to the root logger
    logger.addHandler(stream_h)
    logger.addHandler(file_h)
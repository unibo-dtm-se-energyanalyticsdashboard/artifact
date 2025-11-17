import logging
from logging.handlers import RotatingFileHandler
import os # Import the os module

def setup_logging(level: str = "INFO") -> None:
    logger = logging.getLogger()
    if logger.handlers:
        return

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt) # Create formatter

    # --- Console Handler ---
    stream_h = logging.StreamHandler()
    stream_h.setFormatter(formatter) # Use the formatter
    logger.addHandler(stream_h)

    # --- File Handler (with directory check) ---
    log_file_path = "logs/app.log"
    
    # Get the directory part of the path
    log_directory = os.path.dirname(log_file_path)
    
    # Create the 'logs/' directory if it does not exist
    if not os.path.exists(log_directory):
        try:
            os.makedirs(log_directory)
        except OSError as e:
            # Handle potential race condition or permission error
            logger.error(f"Could not create log directory: {e}")
            return # Do not add file handler if dir creation fails

    # Now it is safe to create the file handler
    file_h = RotatingFileHandler(log_file_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    file_h.setFormatter(formatter) # Use the formatter
    logger.addHandler(file_h)
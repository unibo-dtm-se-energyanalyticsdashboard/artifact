import logging
from logging.handlers import RotatingFileHandler

def setup_logging(level: str = "INFO") -> None:
    logger = logging.getLogger()
    if logger.handlers:
        return  # already configured

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    stream_h = logging.StreamHandler()
    stream_h.setFormatter(logging.Formatter(fmt, datefmt))

    file_h = RotatingFileHandler("logs/app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    file_h.setFormatter(logging.Formatter(fmt, datefmt))

    logger.addHandler(stream_h)
    logger.addHandler(file_h)

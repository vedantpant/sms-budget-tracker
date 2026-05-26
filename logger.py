# logger.py — Logging framework with file + console output

import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="budget_tracker", log_file="budget_tracker.log"):
    """Setup logger with file rotation + console output."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler (INFO and above)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S"
    ))

    # File handler (DEBUG and above, rotating 5MB x 3 files)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger

# Global logger instance
log = setup_logger()
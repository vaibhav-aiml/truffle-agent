"""Logging configuration for Truffle."""

import logging
import logging.handlers
from pathlib import Path

def setup_logger(name="truffle"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create data directory if it doesn't exist
    base_dir = Path(__file__).parent.parent.parent
    log_dir = base_dir / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "truffle.log"
    
    # Rotating File Handler — caps log at 5 MB with 3 backups,
    # preventing unbounded disk growth in long-running containers.
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

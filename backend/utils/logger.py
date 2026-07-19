"""Logging configuration for Truffle."""

import logging
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
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
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

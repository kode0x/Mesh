"""
Logging configuration and utilities.

Provides centralized logging setup for the application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure application-wide logging.
    
    Args:
        level: The logging level (default: INFO).
        log_file: Optional path to log file. If None, logs to stdout only.
        
    Returns:
        The configured logger instance.
    """
    logger = logging.getLogger("mesh")
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "mesh") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: The logger name (default: "mesh").
        
    Returns:
        The logger instance.
    """
    return logging.getLogger(name)

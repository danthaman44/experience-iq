"""
Structured logging configuration for the application.
"""

import logging
import sys
from typing import Any, Dict

from .config import settings


def setup_logging() -> logging.Logger:
    """
    Configure and return a structured logger for the application.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Global logger instance
logger = setup_logging()


def log_info(message: str, extra: Dict[str, Any] | None = None) -> None:
    """
    Log an info message with optional extra context.

    Args:
        message: The message to log
        extra: Optional dictionary of extra context
    """
    if extra:
        logger.info(message, extra=extra)
    else:
        logger.info(message)


def log_error(message: str, extra: Dict[str, Any] | None = None) -> None:
    """
    Log an error message with optional extra context.

    Args:
        message: The message to log
        extra: Optional dictionary of extra context
    """
    if extra:
        logger.error(message, extra=extra)
    else:
        logger.error(message)


def log_warning(message: str, extra: Dict[str, Any] | None = None) -> None:
    """
    Log a warning message with optional extra context.

    Args:
        message: The message to log
        extra: Optional dictionary of extra context
    """
    if extra:
        logger.warning(message, extra=extra)
    else:
        logger.warning(message)


def log_debug(message: str, extra: Dict[str, Any] | None = None) -> None:
    """
    Log a debug message with optional extra context.

    Args:
        message: The message to log
        extra: Optional dictionary of extra context
    """
    if extra:
        logger.debug(message, extra=extra)
    else:
        logger.debug(message)

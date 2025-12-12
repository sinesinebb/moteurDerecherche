# src/utils/logger.py
import logging
import sys
from logging import Logger
from typing import Optional


def setup_logger(name: str = "indexing-service", level: str = "INFO") -> Logger:
    """
    Configure and return a logger with a simple, consistent format.
    Safe to call multiple times.
    """
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(lvl)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(lvl)
        fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Avoid propagation to root logger duplicate messages
        logger.propagate = False
    else:
        logger.setLevel(lvl)
    return logger

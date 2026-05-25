"""
Logging Configuration for the Deepfake Detector.
Provides coloured console output and rotating file logs.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from backend.config import LOGS_DIR, LOG_LEVEL

# ── ANSI colour codes for console output ──────────────────────
_COLOURS = {
    "DEBUG": "\033[36m",     # cyan
    "INFO": "\033[32m",      # green
    "WARNING": "\033[33m",   # yellow
    "ERROR": "\033[31m",     # red
    "CRITICAL": "\033[1;31m",  # bold red
    "RESET": "\033[0m",
}


class _ColouredFormatter(logging.Formatter):
    """Formatter that injects ANSI colour codes based on log level."""

    FMT = "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        colour = _COLOURS.get(record.levelname, _COLOURS["RESET"])
        reset = _COLOURS["RESET"]
        record.levelname = f"{colour}{record.levelname}{reset}"
        formatter = logging.Formatter(self.FMT, datefmt=self.DATE_FMT)
        return formatter.format(record)


def setup_logger(
    name: str = "deepfake_detector",
    log_file: str | None = None,
    level: str | None = None,
) -> logging.Logger:
    """
    Create and return a fully configured logger.

    Parameters
    ----------
    name : str
        Logger name (usually module path).
    log_file : str, optional
        Explicit log-file path.  Defaults to ``<LOGS_DIR>/<name>.log``.
    level : str, optional
        Logging level string.  Defaults to ``config.LOG_LEVEL``.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    log_level = getattr(logging, (level or LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(log_level)

    # ── Console handler ───────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(_ColouredFormatter())
    logger.addHandler(console_handler)

    # ── File handler ──────────────────────────────────────────
    os.makedirs(LOGS_DIR, exist_ok=True)
    if log_file is None:
        log_file = os.path.join(LOGS_DIR, f"{name}.log")

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,   # 10 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_fmt = logging.Formatter(
        "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_logger(name: str = "deepfake_detector") -> logging.Logger:
    """Return an existing logger or create a new one."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

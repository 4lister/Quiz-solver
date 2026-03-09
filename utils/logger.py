from __future__ import annotations

from loguru import logger
from pathlib import Path
import sys


def configure_logging(log_dir: Path | None = None) -> None:
    """
    Configure loguru logging with rotation, as per the spec.
    Logs are written to logs/app.log with 10 MB rotation and also to stderr.
    """
    if log_dir is None:
        log_dir = Path(__file__).resolve().parent.parent / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger.remove()  # remove default handler

    # Console handler
    logger.add(sys.stderr, level="INFO", enqueue=True)

    # File handler with rotation
    logger.add(
        log_file,
        rotation="10 MB",
        retention=5,
        compression=None,
        level="DEBUG",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )


__all__ = ["logger", "configure_logging"]


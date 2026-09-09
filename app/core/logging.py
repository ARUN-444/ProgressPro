"""
Logging configuration module for ProgressPro.
Configures clean, structured console logging for development and production.
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Initializes application-wide logging format and level.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


# Module-level logger for use in core components
logger = logging.getLogger("progresspro")

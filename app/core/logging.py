"""Logging setup for the application."""

import logging


def configure_logging() -> None:
    """Configure concise, process-wide logging once at application startup."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

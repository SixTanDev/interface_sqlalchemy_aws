# pylint: disable=C0114
from typing import Optional
from logging import Logger
from sys import stderr
from loguru import logger as loguru_logger


def loguru_adapter(format_message: Optional[str] = None) -> Logger:
    """
    Configures and returns a logging adapter using Loguru.

    Args:
    - format_message (str, optional): The format of the log message. If not provided,
      a default format will be used.

    Returns:
    - Logger: A Logger object configured for logging with Loguru.
    """

    format_message: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "| <level>{level: <8}</level> "
        "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
        "- <level>{message}</level>"
    ) if not format_message else format_message

    loguru_logger.remove()
    loguru_logger.add(
        sink=stderr,
        format=format_message,
    )

    return loguru_logger

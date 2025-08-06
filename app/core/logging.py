"""Structured logging configuration for the application."""

import logging
import sys
from typing import Any, Dict
import structlog
from pythonjsonlogger import jsonlogger
from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structured logger
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_request_info(request_id: str, method: str, path: str, **kwargs) -> None:
    """Log request information.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        **kwargs: Additional context
    """
    logger = get_logger("request")
    logger.info(
        "Request started",
        request_id=request_id,
        method=method,
        path=path,
        **kwargs
    )


def log_response_info(request_id: str, status_code: int, duration: float, **kwargs) -> None:
    """Log response information.
    
    Args:
        request_id: Unique request identifier
        status_code: HTTP status code
        duration: Request duration in seconds
        **kwargs: Additional context
    """
    logger = get_logger("response")
    logger.info(
        "Request completed",
        request_id=request_id,
        status_code=status_code,
        duration=duration,
        **kwargs
    )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context.
    
    Args:
        error: Exception to log
        context: Additional context information
    """
    logger = get_logger("error")
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    ) 
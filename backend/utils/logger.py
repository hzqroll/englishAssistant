"""
Logging utilities.

Provides custom JSON formatter for structured logging.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Formats log records as JSON strings for better parsing and analysis.

    Attributes:
        format_fields: List of fields to include in log output
    """

    def __init__(self, format_fields: list = None):
        """
        Initialize JSON formatter.

        Args:
            format_fields: List of fields to include in logs
        """
        super().__init__()
        self.format_fields = format_fields or [
            'timestamp',
            'level',
            'name',
            'message',
            'module',
            'function',
            'line'
        ]

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log string
        """
        # TODO: Implement JSON formatting
        # 1. Create base log dict
        # 2. Add standard fields
        # 3. Add exception info if present
        # 4. Add extra fields from record
        # 5. Serialize to JSON

        log_dict: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                'relativeCreated', 'thread', 'threadName', 'processName',
                'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info'
            }:
                log_dict[key] = value

        return json.dumps(log_dict)


def setup_logging(
    level: str = "INFO",
    format_type: str = "json"
) -> None:
    """
    Setup application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type (json or text)
    """
    # TODO: Implement logging setup
    # 1. Get root logger
    # 2. Set log level
    # 3. Create handler (console or file)
    # 4. Set formatter
    # 5. Add handler to logger

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    console_handler = logging.StreamHandler()

    # Set formatter
    if format_type == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )

    # Add handler to logger
    root_logger.addHandler(console_handler)

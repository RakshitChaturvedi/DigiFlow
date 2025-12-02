from logging.config import dictConfig
import logging


class TraceIdFilter(logging.Filter):
    # ensure every log record always has trace_id
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "trace_id"):
            record.trace_id = "-"
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"trace_id_filter": {"()": "app.core.logging.TraceIdFilter"}},
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] [trace_id=%(trace_id)s] %(message)s",
        },
        "uvicorn": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["trace_id_filter"],
        },
        "uvicorn": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.asgi": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
    },
}


def setup_logging():
    dictConfig(LOGGING_CONFIG)

from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] [trace_id=%(trace_id)s] %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}


def setup_logging():
    dictConfig(LOGGING_CONFIG)

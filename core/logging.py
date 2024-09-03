import logging

from .settings import LOG_LEVEL


config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s|%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "default"
        }
    },
    "loggers": {
        "main": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING"
    }
}
logging.config.dictConfig(config)
log = logging.getLogger("main")

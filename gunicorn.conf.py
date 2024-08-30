# https://docs.gunicorn.org/en/stable/settings.html
import os
from pathlib import Path

from uvicorn.workers import UvicornWorker

bind = ":".join(("0.0.0.0", os.getenv("PORT", "8000")))
workers = int(os.getenv("WORKERS", 4))
max_requests = 500000
worker_class = UvicornWorker

log_dir = Path("/data/var/log")
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO"},
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(levelprefix)s %(message)s",
        },
        "access": {
            "()": "src.log_formatter.CustomFormatter",
            "fmt": "%(asctime)s - %(elapsed).2f - %(levelprefix)s %(client_addr)s - "
            '"%(request_line)s" %(status_code)s',
        },
        "chatbot": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s [%(process)d] %(levelprefix)s %(module)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / "chatbot_api.log.stderr",
            "maxBytes": 1024 * 1024 * 100,
            "backupCount": 10,
        },
        "access": {
            "formatter": "access",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / "chatbot_api.log.stderr",
            "maxBytes": 1024 * 1024 * 100,
            "backupCount": 10,
        },
        "chatbot": {
            "formatter": "chatbot",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / "chatbot_api.log.stdout",
            "maxBytes": 1024 * 1024 * 100,
            "backupCount": 10,
        },
    },
    "loggers": {
        "gunicorn.error": {"level": "INFO", "handlers": ["default"], "propagate": False},
        "gunicorn.access": {"handlers": ["access"], "level": "DEBUG", "propagate": False},
        "chatbot": {"handlers": ["chatbot"], "level": "INFO", "propagate": False},
    },
}

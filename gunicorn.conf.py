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
            "()": "src.log_formatter.JsonFormatter",
            "fmt": "{asctime} - {levelprefix} {message}",
            "style": "{",
        },
        "access": {
            "()": "src.log_formatter.JsonFormatter",
            "fmt": "{asctime} - {elapsed} - {levelprefix} {client_addr} - "
            '"{request_line}" {status_code}',
            "style": "{",
        },
        "chatbot": {
            "()": "src.log_formatter.JsonFormatter",
            "fmt": "{asctime} [{process}] {levelprefix} {module}:{lineno} - {message}",
            "style": "{",
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
        "chatbot": {"handlers": ["chatbot"], "level": "INFO", "propagate": False},
        "chatbot.access": {"handlers": ["access"], "level": "DEBUG", "propagate": False},
    },
}

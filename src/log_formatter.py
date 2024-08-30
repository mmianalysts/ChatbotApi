import logging
import sys
import time

from uvicorn.logging import AccessFormatter


class CustomFormatter(AccessFormatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        record.__dict__["elapsed"] = (time.time() - record.created) * 1000
        return super().formatMessage(record)

    def should_use_colors(self) -> bool:
        return sys.stderr.isatty()  # pragma: no cover

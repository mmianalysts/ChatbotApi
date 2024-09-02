import json
import logging
import time
from copy import copy


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
            record.exc_info = None

        record_dict = copy(record.__dict__)
        args = record_dict.pop("args", [])
        if args:
            if record_dict["msg"] == ("Input: %s\nReply: %s") and len(args) == 2:
                record_dict.update(zip(["prompt", "reply"], args))
            if len(args) == 5:
                record_dict.update(
                    zip(["client_addr", "method", "full_path", "http_version", "status_code"], args)
                )
            record_dict["msg"] = record.getMessage()
        record_dict["duration"] = (time.time() - record_dict["created"]) * 1000
        if self.usesTime():
            record_dict["asctime"] = self.formatTime(record, self.datefmt)
        if record_dict["exc_text"]:
            record_dict["msg"] = f"{record_dict['msg']}\n{record_dict['exc_text']}"
            record_dict["exc_text"] = ""
        return json.dumps(record_dict, ensure_ascii=False, separators=(",", ":"))

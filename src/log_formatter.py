import json
import logging
from copy import copy


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
            record.exc_info = None

        record_dict = copy(record.__dict__)
        args = record_dict.pop("args", [])
        if args:
            if record_dict["msg"] == "Input: %s\nReply: %s" and len(args) == 2:
                record_dict.update(zip(["prompt", "reply"], args))
            elif len(args) == 6:
                name = "elapsed", "client", "method", "path", "http_version", "status_code"
                record_dict.update(zip(name, args))
            record_dict["msg"] = record.getMessage()
        if self.usesTime():
            record_dict["asctime"] = self.formatTime(record, self.datefmt)
        if record_dict["exc_text"]:
            record_dict["msg"] = f"{record_dict['msg']}\n{record_dict['exc_text']}"
            record_dict["exc_text"] = ""
        return json.dumps(record_dict, ensure_ascii=False, separators=(",", ":"))

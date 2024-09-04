import logging
import time
from functools import wraps

logger = logging.getLogger("chatbot")


def log_completion_duration(func):
    record_params = ("text", "model", "service")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        reply = await func(*args, **kwargs)
        duration = time.time() - start
        extra = {"duration": duration, "reply": reply}
        extra.update(zip(record_params, args))
        extra.update({k: v for k, v in kwargs.items() if k in record_params[len(args) :]})
        extra["prompt"] = extra.pop("text", "")
        logger.info("Prompt: {prompt}\nReply: {reply}", extra=extra)
        return reply

    return wrapper
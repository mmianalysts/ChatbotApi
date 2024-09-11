import inspect
import logging
import time
from functools import cache, wraps
from typing import Callable

logger = logging.getLogger("chatbot")


@cache
def get_parameter(func: Callable):
    sig = inspect.signature(func)
    parameters_name = sig.parameters.keys()
    return parameters_name


def log_completion_info(*record_params):
    """装饰器函数，记录装饰的异步函数的完成信息。
    Args：
        record_params (str)：要记录在日志中的参数名。
    Return：
        装饰的异步函数。
    示例：
        @log_completion_info("param1", "param2")
        async def my_function(param1, param2):
            # 函数实现
    日志包括以下信息：
    - Duration：装饰函数完成所花费的时间，以毫秒为单位。
    - Reply：装饰函数返回的回复。
    - record_params：其他记录的值。
    日志使用logger.info()方法写入。
    """

    def _inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            res = await func(*args, **kwargs)
            reply, usage = res
            duration = (time.time() - start) * 1000
            extra = {"duration": duration, "reply": reply}
            parameters = get_parameter(func)
            extra.update(
                {name: arg for name, arg in zip(parameters, args) if name in record_params}
            )
            extra.update({k: v for k, v in kwargs.items() if k in record_params[len(args) :]})
            extra["prompt"] = extra.pop("text", "")
            extra.update(dict(usage))
            logger.info("Prompt: {prompt}\nReply: {reply}", extra=extra)
            return res

        return wrapper

    return _inner

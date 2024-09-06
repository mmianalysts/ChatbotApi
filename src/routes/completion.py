import logging
from asyncio.locks import Semaphore
from typing import Optional, Union

import tiktoken
from fastapi import APIRouter, Body
from openai import APIError
from pydantic import BaseModel, model_validator
from tqdm.asyncio import tqdm

from src.retrieve_text import chatbot_openai
from src.schema import ServiceProvider

router = APIRouter(tags=["基础文本"])

logger = logging.getLogger("chatbot")


# lock作为全局变量，在python3.9中会导致Semaphore挂载到不同的loop中，使用延迟加载的方式解决
class Lock:
    def __init__(self, max_num: int):
        self.max_num = max_num
        self._lock = None

    async def __aenter__(self):
        if self._lock is None:
            self._lock = Semaphore(self.max_num)
        return await self._lock.__aenter__()

    async def __aexit__(self, *args):
        if self._lock is None:
            return
        return await self._lock.__aexit__(*args)


lock = Lock(100)


class BaseCompletionReq(BaseModel):
    model: str = Body(description="模型名称, 可用模型取决于选择的服务商")
    service: ServiceProvider = Body(default="openai", description="LLM服务供应商")
    api_key: str = Body(
        default="",
        alias="OPENAI_API_KEY",
        deprecated=True,
        description="OpenAI API Key",
    )
    temperature: float = Body(0, description="温度参数，默认为0", ge=0, le=1)

    @model_validator(mode="after")
    def compatible_client(self):
        if self.api_key.startswith("sk-"):
            self.service = "openai"
        if self.service == "minimax" and self.temperature == 0:
            self.temperature = 1e-5
        return self


class CompletionReq(BaseCompletionReq):
    text: str = Body(description="输入的文本")


class BatchCompletionReq(BaseCompletionReq):
    prompts: list[str] = Body(description="输入的文本列表")


class CompletionWithImgReq(CompletionReq):
    pic: Optional[str] = Body(default=None, description="图片链接或base64编码")


@router.post("/gpt_openai", description="基础问答功能，可以输入图片")
async def gpt_openai(body: CompletionWithImgReq):
    data = body.model_dump() | {"status": "ok"}
    data["reply"], data["usage"] = await chatbot_openai(
        body.text, body.model, body.service, pic=body.pic, temperature=body.temperature
    )
    return data


@router.post("/gpt_openai_v2", deprecated=True, description="指向'/gpt_openai', 但服务商为azure")
async def gpt_openai_v2(body: CompletionWithImgReq):
    body.service = "azure"
    return await gpt_openai(body)


@router.post("/gpt_openai_fast", description="批量调用文本补全")
async def gpt_openai_fast(body: BatchCompletionReq):
    data = {}

    async def get_result(prompt):
        try:
            async with lock:
                return "ok", await chatbot_openai(prompt, model=body.model, service=body.service)
        except APIError as e:
            logger.error(f"Batch completion error: {e}")
            return "error", e.message

    results = await tqdm.gather(*[get_result(prompt) for prompt in body.prompts])
    data["prompts"] = body.prompts
    data["status"] = [result[0] for result in results]
    data["reply"] = [result[1] for result in results]
    return data


@router.post("/get_token_num", description="获取文本token数量")
def bot_token_num(
    text: Union[str, list[str]] = Body(description="输入文本或文本列表"),
    model: str = Body(default="gpt-3.5-turbo", description="模型名称"),
):
    result = {"text": text, "status": "ok", "reply": 0}
    if not isinstance(text, list):
        text = [text]
    encoding = tiktoken.encoding_for_model(model)
    result["reply"] = [len(token) for token in encoding.encode_batch(text)]
    if len(text) == 1:
        result["reply"] = result["reply"][0]
    return result

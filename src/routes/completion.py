import logging
import re
from asyncio.locks import Semaphore
from typing import Optional, Union

import tiktoken
from fastapi import APIRouter, Body
from openai import NOT_GIVEN, APIError
from openai.types.shared_params.response_format_json_schema import JSONSchema
from pydantic import BaseModel, Field, field_validator, model_validator
from tqdm.asyncio import tqdm

from src.retrieve_text import chatbot_openai
from src.schema import ResponseFormat, ServiceProvider

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
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    model: str = Body(description="模型名称, 可用模型取决于选择的服务商")
    service: ServiceProvider = Body(default="openai", description="LLM服务供应商")
    api_key: str = Body(
        default="",
        alias="OPENAI_API_KEY",
        deprecated=True,
        description="OpenAI API Key",
    )
    temperature: float = Body(0, description="温度参数，默认为0", ge=0, le=1)
    seed: Optional[int] = Body(default=None, description="随机种子，仅支持openai")
    json_mode: Union[bool, JSONSchema] = Body(
        None,
        description="True表示启用json模式，或者传入json_schema指定响应的json的格式, 仅支持openai。"
        "文档：https://platform.openai.com/docs/api-reference/chat/create",
    )

    @property
    def response_format(self) -> ResponseFormat:
        if self.service != "openai":
            return NOT_GIVEN
        if not self.json_mode:
            return NOT_GIVEN
        if self.json_mode is True:
            return {"type": "json_object"}
        return {"type": "json_schema", "json_schema": self.json_mode}

    @model_validator(mode="after")
    def compatible_client(self):
        if self.api_key.startswith("sk-"):
            self.service = "openai"
        if self.service == "minimax" and self.temperature == 0:
            self.temperature = 1e-5

        if self.__pydantic_extra__:  # 移除alias
            for field in self.model_fields.values():
                if field.alias:
                    self.__pydantic_extra__.pop(field.alias, None)
        return self


class CompletionReq(BaseCompletionReq):
    text: str = Body(description="输入的文本")
    system: str = Body(default="", description="系统提示词，默认为空")
    pic: Optional[str] = Field(
        default=None,
        description="图片链接或base64编码后的字符串",
        pattern=re.compile(r"https?://|[\w+\=]+$", re.ASCII),
    )
    messages: list[dict] = Body(
        default_factory=list,
        description="复杂消息或多轮对话可以使用此参数。 如果为空，会自动将text, system, pic参数解析为message列表。"
        "如果不为空，会忽略text, system, pic参数。",
    )

    @field_validator("pic")
    @classmethod
    def fix_pic_url(cls, pic):
        if not pic.startswith("http"):
            return "data:image/jpeg;base64," + pic
        return pic

    @model_validator(mode="after")
    def compatible_message(self):
        if self.messages:
            return self
        if self.system:
            self.messages.append({"role": "system", "content": self.system})
        if self.text:
            content = self.text
            if self.pic:
                content = [
                    {"type": "text", "text": self.text},
                    {"type": "image_url", "image_url": {"url": self.pic}},
                ]
            self.messages.append({"role": "user", "content": content})
        return self


class BatchCompletionReq(BaseCompletionReq):
    prompts: list[str] = Body(description="输入的文本列表")
    system: str = Body(default="", description="系统提示词，默认为空")
    messages_list: list[list[dict]] = Body(
        default_factory=list, description="复杂消息或多轮对话可以使用此参数。"
    )

    @model_validator(mode="after")
    def compatible_message(self):
        if self.messages_list:
            return self
        self.messages_list = [[{"role": "user", "content": prompt} for prompt in self.prompts]]
        if self.system:
            for message in self.messages_list:
                message.insert(0, {"role": "system", "content": self.system})
        return self


@router.post(
    "/gpt_openai",
    description="基础问答功能，可以输入图片。除了scheme中的参数外，其他请求参数也会转发给对应的服务。",
)
async def gpt_openai(body: CompletionReq):
    data = body.model_dump() | {"status": "ok"}
    data["reply"], data["usage"] = await chatbot_openai(
        body.messages,  # type: ignore
        body.model,
        body.service,
        temperature=body.temperature,
        seed=body.seed,
        response_format=body.response_format,
        **body.__pydantic_extra__ or {},
    )
    return data


@router.post("/gpt_openai_v2", deprecated=True, description="指向'/gpt_openai', 但服务商为azure")
async def gpt_openai_v2(body: CompletionReq):
    body.service = "azure"
    return await gpt_openai(body)


@router.post("/gpt_openai_fast", description="批量调用文本补全")
async def gpt_openai_fast(body: BatchCompletionReq):
    data = body.model_dump()

    async def get_result(messages: list[dict]):
        try:
            async with lock:
                return "ok", await chatbot_openai(
                    messages,  # type: ignore
                    model=body.model,
                    service=body.service,
                    temperature=body.temperature,
                    seed=body.seed,
                    response_format=body.response_format,
                    **body.__pydantic_extra__ or {},
                )
        except APIError as e:
            logger.error(f"Batch completion error: {e}")
            return "error", e.message

    results = await tqdm.gather(*[get_result(messages) for messages in body.messages_list])
    data["status"] = [result[0] for result in results]
    data["reply"] = [result[1][0] for result in results]
    data["usage"] = [result[1][1] for result in results]
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

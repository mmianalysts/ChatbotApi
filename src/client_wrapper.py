"""
文件包含了对其他客户端的封装，使得调用方式与OpenAI的客户端一致
"""

import time

from anthropic import AsyncAnthropic
from anthropic.types import ContentBlock, Message, TextBlock
from openai import NOT_GIVEN, AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage


def claude_block_to_openai_message(block: ContentBlock) -> ChatCompletionMessage:
    if isinstance(block, TextBlock):
        return ChatCompletionMessage(content=block.text, role="assistant")
    # not support tool call for claude
    raise ValueError(f"Unsupported block type: {block}")


class AsyncClaude(AsyncOpenAI):
    def __init__(self, api_key: str, **kwargs):
        self.client = AsyncAnthropic(api_key=api_key, **kwargs)

    @property
    def chat(self):  # type: ignore
        return self

    @property
    def completions(self):  # type: ignore
        return self

    async def create(self, **kwargs):
        kwargs.setdefault("max_tokens", 4096)
        kwargs = {k: v for k, v in kwargs.items() if v not in (None, NOT_GIVEN)}
        res: Message = await self.client.messages.create(**kwargs)
        return ChatCompletion(
            id=res.id,
            choices=[
                Choice(
                    index=i,
                    finish_reason="stop",
                    message=claude_block_to_openai_message(block),
                )
                for i, block in enumerate(res.content)
            ],
            created=int(time.time() * 1000),
            model=res.model,
            object="chat.completion",
            usage=CompletionUsage(
                completion_tokens=res.usage.output_tokens,
                prompt_tokens=res.usage.input_tokens,
                total_tokens=res.usage.output_tokens + res.usage.input_tokens,
            ),
        )

    @property
    def embedded(self):
        raise NotImplementedError("Claude does not support embedded completions")
